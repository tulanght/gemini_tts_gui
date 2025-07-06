import re
import datetime
from pathlib import Path

def update_constants_file(file_path, new_version):
    """Cập nhật phiên bản trong file constants.py."""
    try:
        content = file_path.read_text(encoding='utf-8')
        pattern = re.compile(r"APP_VERSION\s*=\s*['\"].+?['\"]")
        new_content = pattern.sub(f'APP_VERSION = "{new_version}"', content, count=1)
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Đã cập nhật phiên bản trong: {file_path.name}")
        else:
            print(f"⚠️ Không tìm thấy dòng APP_VERSION trong: {file_path.name}")
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật {file_path.name}: {e}")

def update_readme_file(file_path, new_version):
    """Cập nhật phiên bản trong file README.md."""
    try:
        content = file_path.read_text(encoding='utf-8')
        # Tìm dòng: # Gemini Creative Suite vX.X.X
        pattern = re.compile(r"(# Gemini Creative Suite v)\d+\.\d+\.\d+")
        # SỬA LỖI: Sử dụng r"\g<1>" để tham chiếu group một cách an toàn và rõ ràng
        new_content = pattern.sub(r"\g<1>" + new_version, content, count=1)
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Đã cập nhật phiên bản trong: {file_path.name}")
        else:
            print(f"⚠️ Không tìm thấy tiêu đề phiên bản trong: {file_path.name}")
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật {file_path.name}: {e}")

def update_changelog_file(file_path, new_version):
    """Chèn một mục phiên bản mới vào đầu file CHANGELOG.md."""
    try:
        today = datetime.date.today().isoformat()
        new_section = f"""## [{new_version}] - {today}

### Đã thêm (Added)
- 

### Đã thay đổi (Changed)
- 

### Đã sửa (Fixed)
- 

"""
        content = file_path.read_text(encoding='utf-8')
        # Tìm vị trí để chèn, ngay sau dòng "Dự án này tuân theo..."
        insertion_point = re.search(r"(\[Keep a Changelog\]\(.*\)\.\n)", content)
        if insertion_point:
            position = insertion_point.end()
            new_content = content[:position] + "\n" + new_section + content[position:]
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Đã chèn mục mới cho v{new_version} vào: {file_path.name}")
        else:
            print(f"⚠️ Không tìm thấy điểm chèn trong: {file_path.name}")

    except Exception as e:
        print(f"❌ Lỗi khi cập nhật {file_path.name}: {e}")


def main():
    project_root = Path(__file__).parent.parent
    constants_file = project_root / "src" / "gemini_tts_app" / "constants.py"
    readme_file = project_root / "README.md"
    changelog_file = project_root / "CHANGELOG.md"

    try:
        content = constants_file.read_text(encoding='utf-8')
        current_version = re.search(r"APP_VERSION\s*=\s*['\"](.+?)['\"]", content).group(1)
    except (FileNotFoundError, AttributeError):
        print("❌ LỖI: Không tìm thấy 'APP_VERSION' trong constants.py!")
        return

    print(f"Phiên bản hiện tại là: {current_version}")
    new_version = input(f"Nhập phiên bản mới (ví dụ: 1.0.3): ").strip()

    if not new_version or new_version == current_version:
        print("Đã hủy. Không có gì thay đổi.")
        return

    print("-" * 30)
    print(f"🚀 Bắt đầu nâng cấp phiên bản từ {current_version} lên {new_version}...")

    # Thực hiện cập nhật
    update_constants_file(constants_file, new_version)
    update_readme_file(readme_file, new_version)
    update_changelog_file(changelog_file, new_version)

    print("-" * 30)
    print("✨ Hoàn tất!")
    print("👉 Hành động tiếp theo: Mở file CHANGELOG.md và điền vào các thay đổi chi tiết cho phiên bản mới.")

if __name__ == "__main__":
    main()