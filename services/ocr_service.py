# portfolio\services\ocr_service.py

from paddleocr import PaddleOCR


class OCRService:

    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="en"
    )

    @staticmethod
    def extract_text(image_path: str) -> str:

        result = OCRService.ocr.ocr(image_path)

        text = []

        for line in result[0]:

            text.append(
                line[1][0]
            )

        return "\n".join(text)