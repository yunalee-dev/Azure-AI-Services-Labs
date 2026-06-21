import cv2
import gradio as gr

from face_detection import detect_faces_in_image


def detect_faces_for_gradio(input_image):
    """
    Gradio에서 업로드한 이미지를 받아 얼굴 감지 결과를 반환합니다.

    Gradio 이미지는 RGB 형식이고,
    OpenCV는 기본적으로 BGR 형식을 사용합니다.
    그래서 RGB -> BGR -> 얼굴 감지 -> RGB 순서로 변환합니다.
    """

    if input_image is None:
        return None, "이미지를 업로드해 주세요."

    image_bgr = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)

    result_bgr, faces = detect_faces_in_image(image_bgr)

    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)

    message = f"감지된 얼굴 수: {len(faces)}개"

    return result_rgb, message


demo = gr.Interface(
    fn=detect_faces_for_gradio,
    inputs=gr.Image(
        type="numpy",
        label="얼굴 감지할 이미지 업로드",
    ),
    outputs=[
        gr.Image(
            type="numpy",
            label="얼굴 감지 결과",
        ),
        gr.Textbox(
            label="감지 결과 요약",
        ),
    ],
    title="OpenCV Haar Cascade Face Detection",
    description=(
        "이미지를 업로드하면 OpenCV Haar Cascade로 얼굴을 감지하고 "
        "얼굴 위치에 Bounding Box를 표시합니다."
    ),
)


if __name__ == "__main__":
    demo.launch()