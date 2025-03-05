from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import requests
import os
import json
from cryptography.fernet import Fernet

PRODUCT_ID = "" # Gumroad Product ID here
ENCRYPTION_KEY = Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)
LICENSE_PATH = "license.dat"


class LicenseWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("License Activation")
        self.setGeometry(400, 200, 300, 200)
        self.initUI()
        self.checkSavedLicense()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Activation Software")
        layout.addWidget(self.label)

        self.emailInput = QLineEdit(self)
        self.emailInput.setPlaceholderText("Please enter you email here")
        layout.addWidget(self.emailInput)

        self.licenseInput = QLineEdit()
        self.licenseInput.setPlaceholderText("Please copy and paste your key here")
        layout.addWidget(self.licenseInput)

        self.activateButton = QPushButton("Activate")
        self.activateButton.clicked.connect(self.verifyLicense)
        layout.addWidget(self.activateButton)

        self.deactivateButton = QPushButton("Deactivate License")
        self.deactivateButton.clicked.connect(self.deactivateLicense)
        layout.addWidget(self.deactivateButton)

        self.setLayout(layout)

    def verifyLicense(self):
        email = self.emailInput.text()
        license_key = self.licenseInput.text()

        if self.checkLicense(email, license_key, PRODUCT_ID):
            self.saveLicense(license_key)
            QMessageBox.information(self, 'Valid License', 'The license has been verified and saved.')
            self.close()
        else:
            QMessageBox.warning(self, 'Invalid License', 'The license is not valid. Please verify your data.')
            self.deactivateLicense()

    def checkLicense(self, email, license_key, product_id): # email is not really needed
        url = f'https://api.gumroad.com/v2/licenses/verify'
        data = {
            'product_id': product_id,
            'license_key': license_key,
            'email': email
        }
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False) and not result["purchase"].get("refunded", False)
        except Exception as e:
            QMessageBox.critical(self, "Error", "❌ Connection error")
        return False

    def saveLicense(self, licenseKey):
        encryptedLicense = fernet.encrypt(licenseKey.encode())
        with open(LICENSE_PATH, 'wb') as file:
            file.write(encryptedLicense)

    def checkSavedLicense(self):
        if os.path.exists(LICENSE_PATH):
            try:
                with open(LICENSE_PATH, 'rb') as file:
                    encryptedLicense = file.read()
                    licenseKey = fernet.decrypt(encryptedLicense).decode()
                    if self.checkLicense("", licenseKey, PRODUCT_ID):
                        QMessageBox(self, "License", "✔ License is valid!")
                        self.close()
                    else:
                        os.remove(LICENSE_PATH)
            except Exception as e:
                pass

    def deactivateLicense(self):
        warning = QMessageBox.warning(self, "Deactivate License", "Are you sure you want to deactivate the license? You will lose access. To reactivate, re-enter your license key.", QMessageBox.Yes | QMessageBox.No)
        if warning == QMessageBox.Yes:
            if os.path.exists(LICENSE_PATH):
                os.remove(LICENSE_PATH)
                QMessageBox.information(self, "License Deactivated", "License deactivated successfully. Re-enter your license key to regain access. 🔓")
                self.licenseInput.clear()

if __name__ == "__main__":
    app = QApplication([])
    window = LicenseWindow()
    window.show()
    app.exec()
