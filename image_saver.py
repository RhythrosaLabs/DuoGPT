from PyQt5.QtWidgets import QFileDialog


class ImageSaver:
    def save_uploaded_image(self):
        self.save_image(self.uploaded_image_label)

    def save_generated_image(self):
        self.save_image(self.generated_image_label)

    def save_image(self, image_label):
        if image_label.pixmap() is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")
            if file_path:
                image_label.pixmap().save(file_path)