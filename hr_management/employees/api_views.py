from django.http import JsonResponse
from django.db.models import Q, Exists, OuterRef
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import json
import google.generativeai as genai
from decouple import config
from django.utils import timezone
import logging
from .models import Employee, Contract

# Configure Gemini API
genai.configure(api_key=config('GEMINI_API_KEY', default=''))

GROQ_TEXT_MODEL = config('GROQ_TEXT_MODEL', default='openai/gpt-oss-120b')
GEMINI_VISION_MODEL = config('GEMINI_VISION_MODEL', default='gemini-2.5-flash')
MAX_AI_UPLOAD_SIZE = 10 * 1024 * 1024
AI_PARSE_COOLDOWN_SECONDS = 30
logger = logging.getLogger(__name__)


def employee_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)

    today = timezone.now().date()
    active_contracts = Contract.objects.filter(
        employee_id=OuterRef('pk'),
        is_active=True,
        start_date__lte=today,
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    )

    employees = Employee.objects.filter(
        Q(code__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(full_name__icontains=query) |
        Q(email__icontains=query)
    ).filter(
        is_active=True
    ).annotate(
        has_active_contract=Exists(active_contracts)
    ).filter(
        has_active_contract=False
    )[:10]

    results = []
    for employee in employees:
        department_name = ""
        if employee.position and employee.position.department:
            department_name = employee.position.department.name

        results.append({
            'id': employee.id,
            'code': employee.code,
            'full_name': employee.full_name,
            'position': employee.position.name if employee.position else '',
            'department': department_name
        })

    return JsonResponse(results, safe=False)

@login_required
@require_POST
def parse_cv_api(request):
    if 'cv_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy file tải lên'}, status=400)

    if request.POST.get('ai_privacy_consent') != 'on':
        return JsonResponse(
            {'success': False, 'error': 'Bạn cần đồng ý gửi tài liệu tới dịch vụ AI'},
            status=400,
        )
    
    uploaded_file = request.FILES['cv_file']
    mime_type = uploaded_file.content_type
    file_extension = uploaded_file.name.lower().rsplit('.', 1)[-1] if '.' in uploaded_file.name else ''
    allowed_types = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
    }

    if uploaded_file.size > MAX_AI_UPLOAD_SIZE:
        return JsonResponse(
            {'success': False, 'error': 'File không được vượt quá 10 MB'},
            status=400,
        )
    if allowed_types.get(file_extension) != mime_type:
        return JsonResponse(
            {'success': False, 'error': 'Chỉ hỗ trợ file PDF hoặc ảnh JPG, PNG, WEBP'},
            status=400,
        )

    throttle_key = f'ai-parse:{request.user.pk}'
    if not cache.add(throttle_key, True, timeout=AI_PARSE_COOLDOWN_SECONDS):
        return JsonResponse(
            {'success': False, 'error': 'Vui lòng chờ 30 giây trước khi phân tích file tiếp theo'},
            status=429,
        )

    file_data = uploaded_file.read()

    try:
        import io
        
        prompt = """
        Bạn là một hệ thống AI trích xuất thông tin. Hãy đọc tài liệu đính kèm (CV hoặc CCCD) và trích xuất các thông tin sau dưới dạng JSON. Không giải thích gì thêm ngoài cấu trúc JSON.
        Hãy chuẩn hóa các trường thông tin theo đúng định dạng sau:
        
        - first_name: Tên (Ví dụ: "Hải" trong "Nguyễn Văn Hải")
        - last_name: Họ và tên đệm (Ví dụ: "Nguyễn Văn" trong "Nguyễn Văn Hải")
        - gender: Chỉ được chọn một trong các giá trị: "male" (nếu là Nam), "female" (nếu là Nữ), hoặc "other" (nếu là Khác)
        - date_of_birth: Ngày sinh định dạng YYYY-MM-DD
        - id_number: Số CMND hoặc CCCD (nếu có)
        - phone: Số điện thoại (chỉ lấy số)
        - email: Địa chỉ email
        - address: Địa chỉ thường trú hoặc địa chỉ hiện tại
        - education_level: Chỉ chọn một trong các giá trị tương ứng:
            "high_school" (THPT), "college" (Cao đẳng), "university" (Đại học), "master" (Thạc sĩ), "phd" (Tiến sĩ)
        - degree: Bằng cấp (Ví dụ: Cử nhân, Kỹ sư, Thạc sĩ khoa học...)
        - major: Chuyên ngành học (Ví dụ: Công nghệ thông tin, Quản trị kinh doanh...)
        - graduation_year: Năm tốt nghiệp (số nguyên)
        - graduation_place: Trường tốt nghiệp
        - ranking: Xếp loại học tập (Ví dụ: Xuất sắc, Giỏi, Khá, Trung bình)
        """
        
        if mime_type == 'application/pdf':
            from groq import Groq
            groq_api_key = config('GROQ_API_KEY', default='')
            if not groq_api_key:
                return JsonResponse(
                    {'success': False, 'error': 'Chưa cấu hình GROQ_API_KEY'},
                    status=500,
                )
            client = Groq(api_key=groq_api_key)
            import pypdf
            pdf = pypdf.PdfReader(io.BytesIO(file_data))
            text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nDữ liệu CV/CCCD:\n{text}",
                    }
                ],
                model=GROQ_TEXT_MODEL,
                response_format={"type": "json_object"},
            )
            response_content = chat_completion.choices[0].message.content
        else:
            if not config('GEMINI_API_KEY', default=''):
                return JsonResponse(
                    {'success': False, 'error': 'Chưa cấu hình GEMINI_API_KEY để phân tích ảnh'},
                    status=500,
                )
            vision_model = genai.GenerativeModel(GEMINI_VISION_MODEL)
            vision_response = vision_model.generate_content([
                prompt,
                {'mime_type': mime_type, 'data': file_data},
            ])
            response_content = vision_response.text
        
        parsed_data = json.loads(response_content)
        return JsonResponse({'success': True, 'data': parsed_data})
        
    except Exception:
        logger.exception('AI CV parsing failed for user_id=%s', request.user.pk)
        return JsonResponse(
            {'success': False, 'error': 'Không thể phân tích tài liệu lúc này. Vui lòng thử lại sau.'},
            status=502,
        )
