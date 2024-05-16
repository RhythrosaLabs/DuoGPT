from PyQt5.QtWidgets import QFileDialog

class ImageUploader:
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Assuming `display_image` is a method to display the image in your application
            self.display_image(file_path)
