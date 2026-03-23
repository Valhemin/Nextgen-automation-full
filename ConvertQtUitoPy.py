import subprocess


def convert_ui(ui_file, output_ui_file, qrc_file, output_qrc_file):
    try:
        ui_command = f"pyside6-uic {ui_file} -o {output_ui_file}"
        subprocess.run(ui_command, shell=True, check=True, capture_output=True, text=True)
        print("Conversion UI successful!")
        # qrc_command = f"pyside6-rcc {qrc_file} -o {output_qrc_file}"
        # subprocess.run(qrc_command, shell=True, check=True, capture_output=True, text=True)
        # print("Conversion QRC successful!")

    except subprocess.CalledProcessError as e:
        print("Error:", e)


if __name__ == "__main__":
    ui_file = "./design/mainWindow.ui"  # Thay your_ui_file.ui bằng đường dẫn đến tệp UI của bạn
    output_ui_file = "./src/ui/MainWindow_ui.py"  # Thay generated_ui.py bằng tên file Python bạn muốn tạo
    qrc_file = "./design/icon/icon.qrc"
    output_qrc_file = "./src/ui/icon_rc.py"
    convert_ui(ui_file, output_ui_file, qrc_file, output_qrc_file)

