from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

app = QApplication([])

window = QWidget()
window.setWindowTitle('PyQt 示例')
layout = QVBoxLayout()

label = QLabel('你好，世界！')
layout.addWidget(label)

window.setLayout(layout)
window.show()

app.exec_()