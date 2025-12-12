from __future__ import annotations
import io
import collections, itertools, re
from collections.abc import Sequence
from typing import Optional, Union
from reedsolo import RSCodec
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QCheckBox, QDialog
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
import numpy as np
import sys
from qr_generator2 import QrCode, QrSegment, DataTooLongError

encoding = "utf-8-sig"

class QRCodeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Generator")
        self.setGeometry(100, 100, 600, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.warning_label = QLabel(
            "警告：请确保输入的文本安全，扫描未知 QR 码可能导致钓鱼或恶意链接风险！"
        )
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setWordWrap(True)
        main_layout.addWidget(self.warning_label)

        # 显示步骤解释复选框
        self.explain_checkbox = QCheckBox("显示创建步骤解释")
        main_layout.addWidget(self.explain_checkbox)

        # 输入字段
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("输入 URL（可选）")
        main_layout.addWidget(self.url_entry)

        self.text_entry = QLineEdit()
        self.text_entry.setPlaceholderText("输入文本（可选）")
        main_layout.addWidget(self.text_entry)

        self.note_entry = QLineEdit()
        self.note_entry.setPlaceholderText("输入备注（可选）")
        main_layout.addWidget(self.note_entry)

        self.generate_button = QPushButton("生成 QR 码")
        self.generate_button.clicked.connect(self.generate_qr)
        main_layout.addWidget(self.generate_button)

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.qr_label)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # 支持版本容量
        self.version_capacities = {1: 25, 2: 47}
        self.show_data_protection_warning()

    def show_data_protection_warning(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("数据保护和安全提示")
        msg.setText(
            "本程序仅在本地生成 QR 码，不会存储或上传您的输入数据。\n"
            "请注意：\n"
            "- 仅输入您信任的文本或 URL。\n"
            "- 扫描 QR 码前，检查其内容，避免钓鱼或恶意链接。\n"
            "- 本程序生成的 QR 码仅为黑白模块，用于显示和扫描。"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def generate_qr(self):
        input_texts = [
            self.url_entry.text().strip(),
            self.text_entry.text().strip(),
            self.note_entry.text().strip()
        ]
        input_text = "; ".join(t for t in input_texts if t)
        if not input_text:
            self.qr_label.setText("请输入至少一个文本或 URL")
            self.status_label.setText("")
            return
        try:
            # 选择版本
            input_length = len(input_text.encode('utf-8'))
            version = 1 if input_length <= self.version_capacities[1] else 2 if input_length <= self.version_capacities[2] else None
            if version is None:
                raise DataTooLongError(f"输入过长 ({input_length} 字节)。最大支持 {self.version_capacities[2]} 字节。")
            self.status_label.setText(f"使用 QR 版本 {version}")

            qr = QrCode.encode_text(input_text, QrCode.Ecc.LOW, minversion=1, maxversion=2, mask=-1)
            data_bytes = input_text.encode('utf-8')
            rs = RSCodec(QrCode._ECC_CODEWORDS_PER_BLOCK[QrCode.Ecc.LOW.ordinal][version])
            rs_codewords = rs.encode(data_bytes)[len(data_bytes):]
            matrix = np.array([[qr.get_module(x, y) for x in range(qr.get_size())] for y in range(qr.get_size())], dtype=int)

            qr_image = qr.to_image(scale=10, border=4)
            qr_image.save("qr_code.png")
            pixmap = QPixmap("qr_code.png")
            self.qr_label.setFixedSize(pixmap.width(), pixmap.height())
            self.qr_label.setPixmap(pixmap)

            if self.explain_checkbox.isChecked():
                self.show_explanation(input_text, data_bytes, rs_codewords, matrix, qr.get_mask())
                
            self.save_intermediate_data(input_text, data_bytes, rs_codewords, matrix, qr.get_mask())

        except DataTooLongError as e:
            QMessageBox.critical(self, "错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成 QR 码失败: {str(e)}")

    def show_explanation(self, text, data_bytes, rs_codewords, matrix, mask):
        dialog = QDialog(self)
        dialog.setWindowTitle("生成步骤演示")
        layout = QVBoxLayout(dialog)
        step_label = QLabel()
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(step_label)
        layout.addWidget(image_label)

        btn_layout = QHBoxLayout()
        prev_btn = QPushButton("上一步")
        next_btn = QPushButton("下一步")
        btn_layout.addWidget(prev_btn)
        btn_layout.addWidget(next_btn)
        layout.addLayout(btn_layout)

        steps = []
        steps.append(("步骤 1: 文本编码", f"原始文本: {text}\nUTF-8 字节 (Hex): {data_bytes.hex()}"))
        steps.append(("步骤 2: Reed-Solomon 纠错", f"纠错码字 (Hex): {rs_codewords.hex()}"))
        pil_img = Image.fromarray(matrix * 255).convert('L')
        pil_img = pil_img.resize((matrix.shape[1]*10, matrix.shape[0]*10))
        buf = io.BytesIO()
        pil_img.save(buf, format='PNG')
        qt_img = QImage.fromData(buf.getvalue())
        steps.append(("步骤 3: 原始矩阵", qt_img))
        final_qt = QImage("qr_code.png")
        steps.append((f"步骤 4: 应用掩码 (模式 {mask})", final_qt))

        dialog.steps = steps
        dialog.current = 0

        def update_slide():
            title, content = dialog.steps[dialog.current]
            dialog.setWindowTitle(title)
            if isinstance(content, QImage):
                image_label.setPixmap(QPixmap.fromImage(content))
                step_label.setText("")
            else:
                step_label.setText(content)
                image_label.clear()

        prev_btn.clicked.connect(lambda: setattr(dialog, 'current', max(dialog.current-1, 0)) or update_slide())
        next_btn.clicked.connect(lambda: setattr(dialog, 'current', min(dialog.current+1, len(dialog.steps)-1)) or update_slide())

        update_slide()
        dialog.exec_()
        
    def save_intermediate_data(self, input_text, data_bytes, rs_codewords, matrix, best_mask):
        with open("intermediate_data.txt", "w", encoding="utf-8") as f:
            f.write("Input Text:\n")
            f.write(f"{input_text}\n\n")
            f.write("Encoded Bytes:\n")
            f.write(f"{data_bytes}\n\n")
            f.write("Reed-Solomon Error Correction Codewords (Hex):\n")
            f.write(f"{rs_codewords.hex()}\n\n")
            f.write(f"Mask Matrix (Pattern {best_mask}):\n")
            f.write(f"{matrix}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRCodeApp()
    window.show()
    sys.exit(app.exec_())
