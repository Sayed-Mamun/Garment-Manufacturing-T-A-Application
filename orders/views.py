# orders/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .serializers import UploadedPDFSerializer, OrderSerializer
from .models import UploadedPDF, Order

import PyPDF2
import pytesseract
from PIL import Image
import io

class PDFUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        pdf_serializer = UploadedPDFSerializer(data=request.data)
        if pdf_serializer.is_valid():
            pdf_instance = pdf_serializer.save()
            # Extract data from PDF here
            extracted_data = self.extract_pdf_data(pdf_instance.file.path)
            if extracted_data:
                order_serializer = OrderSerializer(data=extracted_data)
                if order_serializer.is_valid():
                    order = order_serializer.save()
                    pdf_instance.order = order
                    pdf_instance.save()
                    return Response({'order': order_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Failed to extract data'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(pdf_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def extract_pdf_data(self, file_path):
        # Attempt text extraction using PyPDF2
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                # Here you implement parsing of text to extract required fields
                # For demo, let's assume dummy extraction
                data = {
                    'style_number': self.find_field(text, 'Style Number'),
                    'buyer': self.find_field(text, 'Buyer'),
                    'order_quantity': int(self.find_field(text, 'Order Quantity') or 0),
                    'shipment_date': self.find_field(text, 'Shipment Date'),  # parse date as needed
                    'fabric_details': self.find_field(text, 'Fabric Details'),
                    'trim_details': self.find_field(text, 'Trim Details'),
                }
                return data
        except Exception as e:
            # If failed, fallback to OCR (not implemented here for brevity)
            return None

    def find_field(self, text, field_name):
        # Basic implementation: search for field and extract line or value after it
        import re
        pattern = rf'{field_name}[:\s]*([^\n]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
