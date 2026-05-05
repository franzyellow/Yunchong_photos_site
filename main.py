import boto3
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageOps

load_dotenv()

BUCKET = "yunchong-photos"
ACCOUNT_ID = "4af95933cb734e3ad616a5231b52613a"
PUBLIC_URL = "https://pub-6bd4990d82404bd6ba1d28da02eea43e.r2.dev"
PHOTOS_JSON = Path("photos.json")

THUMB_SIZE = (1000, 1000)  # 缩略图最长边上限，保持原始比例


def get_r2_client():
    # 用 .env 里的 key 创建 R2 连接客户端
    # R2 兼容 S3 协议，所以直接用 boto3，只需把 endpoint 指向 Cloudflare
    return boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )


def process_and_upload(client, image_path: Path, year: str):
    # 处理单张图片：原图直接上传，另生成缩略图上传，返回两者的公开 URL
    # 上传路径格式：<year>/full/<filename> 和 <year>/thumb/<filename>.jpg
    stem = image_path.stem
    suffix = image_path.suffix.lower()
    full_key = f"{year}/full/{image_path.name}"
    thumb_key = f"{year}/thumb/{stem}.jpg"

    # 原图直接上传，不做任何压缩
    content_type = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
    client.upload_file(str(image_path), BUCKET, full_key, ExtraArgs={"ContentType": content_type})

    # 单独生成缩略图用于网格展示
    with Image.open(image_path) as img:
        thumb = ImageOps.exif_transpose(img).convert("RGB")  # 修正 EXIF 旋转方向
        thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
        thumb_path = image_path.parent / f"_thumb_{stem}.jpg"
        thumb.save(thumb_path, "JPEG", quality=80)
        client.upload_file(str(thumb_path), BUCKET, thumb_key, ExtraArgs={"ContentType": "image/jpeg"})
        thumb_path.unlink()

    print(f"  uploaded: {full_key}")
    return f"{PUBLIC_URL}/{full_key}", f"{PUBLIC_URL}/{thumb_key}"


def load_photos():
    # 读取现有的 photos.json；如果文件不存在（首次运行），返回空字典
    if PHOTOS_JSON.exists():
        return json.loads(PHOTOS_JSON.read_text())
    return {}


def save_photos(data):
    # 把更新后的数据写回 photos.json，网站读取这个文件来渲染照片
    PHOTOS_JSON.write_text(json.dumps(data, indent=4, ensure_ascii=False))


def upload(folder: str):
    # 主入口：接收一个年份文件夹路径，把里面所有图片上传到 R2，并更新 photos.json
    # 用法：uv run main.py photos/2024
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"folder not found: {folder}")
        sys.exit(1)

    # 用文件夹名作为相册名，例如 ./photos/2024/ 或 ./photos/2020-2021/
    year = folder_path.name

    images = sorted([
        p for p in folder_path.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic"}
    ])

    if not images:
        print("no images found")
        sys.exit(1)

    print(f"uploading {len(images)} images for year {year}...")
    client = get_r2_client()
    data = load_photos()
    data.setdefault(year, [])

    for img_path in images:
        full_url, thumb_url = process_and_upload(client, img_path, year)
        data[year].append({
            "src": full_url,
            "thumb": thumb_url,
            "caption": img_path.stem,
        })

    save_photos(data)
    print(f"done. photos.json updated.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: uv run main.py <folder>")
        print("example: uv run main.py photos/2024")
        sys.exit(1)

    upload(sys.argv[1])
