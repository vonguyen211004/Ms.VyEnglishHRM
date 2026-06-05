from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import google.generativeai as genai
from decouple import config
from .models import Employee

# Configure Gemini API
genai.configure(api_key=config('GEMINI_API_KEY', default=''))


def employee_search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)

    employees = Employee.objects.filter(
        Q(code__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(full_name__icontains=query) |
        Q(email__icontains=query)
    ).filter(is_active=True)[:10]

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

@csrf_exempt
@require_POST
def parse_cv_api(request):
    if 'cv_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy file tải lên'}, status=400)
    
    uploaded_file = request.FILES['cv_file']
    file_data = uploaded_file.read()
    mime_type = uploaded_file.content_type

    try:
        from groq import Groq
        import base64
        import io
        client = Groq(api_key=config('GROQ_API_KEY', default=''))
        
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
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
        else:
            base64_image = base64.b64encode(file_data).decode('utf-8')
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}",
                                }
                            }
                        ]
                    }
                ],
                model="llama-3.2-11b-vision-preview",
            )
        
        parsed_data = json.loads(chat_completion.choices[0].message.content)
        return JsonResponse({'success': True, 'data': parsed_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)