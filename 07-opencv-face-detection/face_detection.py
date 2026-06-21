import argparse
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent

SAMPLE_DATA_DIR = BASE_DIR / "sample-data"
OUTPUT_DIR = BASE_DIR / "outputs"

DEFAULT_IMAGE_PATH = SAMPLE_DATA_DIR / "sample_face.jpg"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "face_detection_result.jpg"


def load_face_cascade():
    """
    OpenCV에 기본 포함된 Haar Cascade 얼굴 분류기를 로딩합니다.
    haarcascade_frontalface_default.xml은 정면 얼굴 감지용 모델입니다.
    """

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    if face_cascade.empty():
        raise RuntimeError(
            "Haar Cascade XML 파일을 불러오지 못했습니다. "
            "opencv-python 설치 상태를 확인해 주세요."
        )

    return face_cascade


def detect_faces_in_image(
    image,
    scale_factor=1.1,
    min_neighbors=5,
    min_size=(30, 30),
):
    """
    OpenCV 이미지에서 얼굴을 감지하고 Bounding Box를 그립니다.

    Parameters
    ----------
    image:
        OpenCV BGR 이미지
    scale_factor:
        이미지를 얼마나 조금씩 줄여가며 얼굴을 찾을지 결정합니다.
        값이 작을수록 더 촘촘히 찾지만 느려질 수 있습니다.
    min_neighbors:
        얼굴 후보 주변에 비슷한 후보가 몇 개 이상 있어야 얼굴로 인정할지 결정합니다.
        값이 클수록 오탐은 줄지만 얼굴을 놓칠 수 있습니다.
    min_size:
        감지할 얼굴의 최소 크기입니다.

    Returns
    -------
    result_image:
        얼굴 위치에 사각형이 그려진 이미지
    faces:
        감지된 얼굴 좌표 목록. 각 좌표는 (x, y, w, h)입니다.
    """

    if image is None:
        raise ValueError("입력 이미지가 None입니다.")

    face_cascade = load_face_cascade()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=min_size,
    )

    result_image = image.copy()

    for x, y, w, h in faces:
        cv2.rectangle(
            result_image,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            3,
        )

    return result_image, faces


def detect_faces_from_file(
    image_path=DEFAULT_IMAGE_PATH,
    output_path=DEFAULT_OUTPUT_PATH,
):
    """
    이미지 파일을 읽어서 얼굴을 감지하고 결과 이미지를 저장합니다.
    """

    image_path = Path(image_path)
    output_path = Path(output_path)

    if not image_path.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(str(image_path))

    if image is None:
        raise RuntimeError(f"이미지를 읽을 수 없습니다: {image_path}")

    result_image, faces = detect_faces_in_image(image)

    cv2.imwrite(str(output_path), result_image)

    print(f"입력 이미지: {image_path}")
    print(f"감지된 얼굴 수: {len(faces)}")
    print(f"결과 이미지 저장 위치: {output_path}")

    for index, (x, y, w, h) in enumerate(faces, start=1):
        print(f"Face {index}: x={x}, y={y}, width={w}, height={h}")

    return result_image, faces


def run_webcam_face_detection(
    camera_index=0,
    scale_factor=1.1,
    min_neighbors=5,
):
    """
    웹캠을 사용해 실시간 얼굴 감지를 수행합니다.
    q 키를 누르면 종료됩니다.
    """

    face_cascade = load_face_cascade()

    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(
            "웹캠을 열 수 없습니다. "
            "카메라 연결 상태나 권한을 확인해 주세요."
        )

    print("웹캠 얼굴 감지를 시작합니다.")
    print("종료하려면 q 키를 누르세요.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=(30, 30),
        )

        for x, y, w, h in faces:
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                3,
            )

            label = "Face"
            cv2.putText(
                frame,
                label,
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        cv2.imshow("OpenCV Haar Cascade Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description="OpenCV Haar Cascade Face Detection"
    )

    parser.add_argument(
        "--mode",
        choices=["image", "webcam"],
        default="image",
        help="image 또는 webcam 모드를 선택합니다.",
    )

    parser.add_argument(
        "--image",
        default=str(DEFAULT_IMAGE_PATH),
        help="얼굴 감지할 이미지 파일 경로입니다.",
    )

    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="결과 이미지를 저장할 경로입니다.",
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="웹캠 번호입니다. 기본값은 0입니다.",
    )

    args = parser.parse_args()

    if args.mode == "image":
        detect_faces_from_file(
            image_path=args.image,
            output_path=args.output,
        )

    elif args.mode == "webcam":
        run_webcam_face_detection(
            camera_index=args.camera,
        )


if __name__ == "__main__":
    main()