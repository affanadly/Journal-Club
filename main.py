import bibtexparser
import os
import shutil
import sys
import subprocess
import PyQt6.QtCore as QtC
import PyQt6.QtGui as QtG
import PyQt6.QtWidgets as QtW
import qdarktheme

from doi2bib import grab_bib

class PosterGenerator(QtW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RCL Journal Club Poster Generator')
        self.setWindowIcon(QtG.QIcon(os.path.join(ROOT, 'media', 'RCRL.png')))
        self.resize(400, 600)
        self.init_ui()

        self.profile_button.clicked.connect(self.set_profile_location)
        self.doi.returnPressed.connect(self.search_bib_from_doi)
        self.search_bib.clicked.connect(self.search_bib_from_doi)
        self.save_button.clicked.connect(self.set_save_location)
        self.reset_button.clicked.connect(self.reset_all_fields)
        self.settings_button.clicked.connect(self.open_settings)
        self.generate_button.clicked.connect(self.generate_poster)

    def init_ui(self):
        layout = QtW.QVBoxLayout()
        layout.addWidget(self.create_logo())
        layout.addLayout(self.create_presenter_details())
        layout.addLayout(self.create_meeting_details())
        layout.addWidget(self.create_presentation_tabs())
        layout.addLayout(self.create_save_section())
        layout.addLayout(self.create_action_buttons())
        widget = QtW.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_logo(self):
        logo = QtW.QLabel()
        logo.setPixmap(QtG.QPixmap(os.path.join(ROOT, 'media', 'RCRL.png')).scaledToHeight(128))
        logo.setAlignment(QtC.Qt.AlignmentFlag.AlignCenter)
        return logo

    def create_presenter_details(self):
        self.presenter = QtW.QLineEdit(placeholderText='Presenter Name')
        self.role = QtW.QComboBox(editable=True)
        self.role.addItems(['PhD Student', 'MSc Student', 'BSc Student'])
        self.role.setCurrentIndex(-1)
        self.invited = QtW.QCheckBox('Invited')
        self.profile = QtW.QCheckBox('Profile Picture')
        self.profile_location = QtW.QLineEdit(placeholderText='Profile Picture Location')
        self.profile_button = QtW.QPushButton('Browse')
        
        layout_role = QtW.QHBoxLayout()
        layout_role.addWidget(self.role, stretch=1)
        layout_role.addWidget(self.invited)
        
        layout_profile = QtW.QHBoxLayout()
        layout_profile.addWidget(self.profile)
        layout_profile.addWidget(self.profile_location)
        layout_profile.addWidget(self.profile_button)
        
        layout = QtW.QFormLayout()
        layout.addRow('Presenter', self.presenter)
        layout.addRow('Role', layout_role)
        layout.addRow(layout_profile)
        return layout

    def create_meeting_details(self):
        self.date = QtW.QDateEdit(
            QtC.QDate.currentDate().addDays(1), 
            calendarPopup=True,
            displayFormat='d MMMM yyyy'
        )
        self.time = QtW.QTimeEdit(
            QtC.QTime.fromString('10:00 AM', 'hh:mm AP'),
            displayFormat='hh:mm AP'
        )
        layout = QtW.QFormLayout()
        layout.addRow('Date', self.date)
        layout.addRow('Time', self.time)
        return layout

    def create_presentation_tabs(self):
        self.doi = QtW.QLineEdit(placeholderText='Article DOI')
        self.search_bib = QtW.QPushButton('Search')
        doi_row = QtW.QHBoxLayout()
        doi_row.addWidget(self.doi)
        doi_row.addWidget(self.search_bib)

        self.bib = QtW.QTextEdit(placeholderText='BibTeX Entry')
        bibliography = QtW.QFormLayout()
        bibliography.addRow('DOI', doi_row)
        bibliography.addRow('BibTeX', self.bib)
        bib_tab = QtW.QWidget()
        bib_tab.setLayout(bibliography)

        self.title = QtW.QTextEdit(placeholderText='Custom Presentation Title')
        custom_title = QtW.QFormLayout()
        custom_title.addRow('Title', self.title)
        title_tab = QtW.QWidget()
        title_tab.setLayout(custom_title)

        self.presentation_tabs = QtW.QTabWidget()
        self.presentation_tabs.addTab(bib_tab, 'Bibliography')
        self.presentation_tabs.addTab(title_tab, 'Custom Title')
        return self.presentation_tabs

    def create_save_section(self):
        self.save_location = QtW.QLineEdit()
        self.save_button = QtW.QPushButton('Save')
        layout = QtW.QHBoxLayout()
        layout.addWidget(QtW.QLabel('Save Location'))
        layout.addWidget(self.save_location)
        layout.addWidget(self.save_button)
        return layout

    def create_action_buttons(self):
        self.generate_button = QtW.QPushButton('Generate Poster')
        self.reset_button = QtW.QPushButton('Reset')
        self.settings_button = QtW.QPushButton('Settings')
        layout = QtW.QHBoxLayout()
        layout.addWidget(self.generate_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.settings_button)
        return layout

    def message_dialog(self, title, message, info=None, details=None):
        dialog = QtW.QMessageBox()
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QtG.QIcon(os.path.join(ROOT, 'media', 'RCRL.png')))
        dialog.setIcon(QtW.QMessageBox.Icon.Warning)
        dialog.setText(message)
        if info:
            dialog.setInformativeText(info)
        if details:
            dialog.setDetailedText(details)
        dialog.exec()
    
    def set_profile_location(self):
        pic_location = QtW.QFileDialog.getOpenFileName(
            self, 'Select Profile Picture', 
            QtC.QStandardPaths.writableLocation(
                QtC.QStandardPaths.StandardLocation.DownloadLocation
            ),
            'Image Files (*.png *.jpg *.jpeg)'
        )
        self.profile_location.setText(pic_location[0])
    
    def search_bib_from_doi(self):
        doi = self.doi.text()
        if doi:
            bib = grab_bib(doi)
            if bib[1] is not None:
                bib = bibtexparser.loads(bib[1])
                for key, value in bib.entries[0].items():
                    bib.entries[0][key] = value.replace('&amp;', '\\&').replace('\u2013', '-')
                self.bib.setText(bibtexparser.dumps(bib))
                self.citekey = bib.entries[0]['ID']
            else:
                QtW.QMessageBox.warning(self, 'BibTeX from DOI Error', bib[0])
        else:
            QtW.QMessageBox.warning(
                self, 'BibTeX from DOI Error', 'DOI field cannot be empty.'
            )

    def set_save_location(self):
        out_name = self.presenter.text().replace(' ', '').replace('.', '')
        out_date = self.date.date().toString('dMMM')
        save_location = QtW.QFileDialog.getSaveFileName(
            self, 'Save Poster', 
            os.path.join(
                QtC.QStandardPaths.writableLocation(
                    QtC.QStandardPaths.StandardLocation.DownloadLocation
                ), f'{out_name}_{out_date}'),
            'PDF Files (*.pdf)'
        )
        self.save_location.setText(save_location[0])
    
    def reset_all_fields(self):
        dialog = QtW.QMessageBox.question(
            self, 'Confirmation', 'Are you sure you want to reset all fields?'
        )
        if dialog == QtW.QMessageBox.StandardButton.Yes:
            self.presenter.clear()
            self.role.setCurrentIndex(-1)
            self.invited.setChecked(False)
            self.date.setDate(QtC.QDate.currentDate().addDays(1))
            self.time.setTime(QtC.QTime.fromString('10:00 AM', 'hh:mm AP'))
            self.doi.clear()
            self.bib.clear()
            self.title.clear()
            self.save_location.clear()
            self.presentation_tabs.setCurrentIndex(0)
    
    def open_settings(self):
        QtG.QDesktopServices.openUrl(QtC.QUrl.fromLocalFile(os.path.join(ROOT, 'latex/')))
    
    def generate_poster(self):
        for field, obj in {
            'Presenter name': self.presenter.text(),
            'Presenter role': self.role.currentText(),
            'Save location': self.save_location.text()
        }.items():
            if not obj:
                QtW.QMessageBox.warning(
                    self, 'Incomplete Fields', f'{field} cannot be empty.'
                )
                return
        if self.profile.isChecked() and not self.profile_location.text():
            QtW.QMessageBox.warning(
                self, 'Incomplete Fields', 'Profile picture location cannot be empty.'
            )
            return
        if self.presentation_tabs.currentIndex() == 0:
            if not self.bib.toPlainText():
                QtW.QMessageBox.warning(
                    self, 'Incomplete Fields', 'BibTeX entry cannot be empty.'
                )
                return
        else:
            if not self.title.toPlainText():
                QtW.QMessageBox.warning(
                    self, 'Incomplete Fields', 'Title cannot be empty.'
                )
                return
        
        if shutil.which('lualatex') is None or shutil.which('biber') is None:
            QtW.QMessageBox.warning(
                self, 'Missing Dependencies', 
                'lualatex and/or biber not found. Please ensure that a TeX distribution is installed and added to your system PATH.'
            )
            return

        with open(os.path.join(ROOT, 'latex', 'input.tex'), 'w') as f:
            try:
                f.write(
                    r'\newcommand{\Presenter}{' + self.presenter.text() + '}\n' +
                    r'\newcommand{\Role}{' + self.role.currentText() + '}\n'
                )
                if self.invited.isChecked():
                    f.write(r'\newcommand{\Invited}{True}' + '\n')
                if self.profile.isChecked() and self.profile_location.text():
                    f.write(
                        r'\newcommand{\Profile}{' + self.profile_location.text().replace('\\', '/') + '}\n'
                    )
                
                f.write(
                    r'\newcommand{\Day}{' + self.date.date().toString('dddd') + '}\n' +
                    r'\newcommand{\Date}{' + self.date.date().toString('d MMMM yyyy') + '}\n' +
                    r'\newcommand{\Time}{' + self.time.time().toString('hh:mm AP') + '}\n'
                )
                if self.presentation_tabs.currentIndex() == 0:
                    f.write(r'\newcommand{\CiteKey}{' + self.citekey + '}\n')
                else:
                    f.write(r'\newcommand{\Title}{' + self.title.toPlainText() + '}\n')
            except:
                QtW.QMessageBox.warning(
                    self, 'Input Error', 'Failed to write input details to file.'
                )
                return
        
        if self.presentation_tabs.currentIndex() == 0:
            with open(os.path.join(ROOT, 'latex', 'ref.bib'), 'w') as f:
                try:
                    f.write(self.bib.toPlainText())
                except:
                    QtW.QMessageBox.warning(
                        self, 'BibTeX Error', 'Failed to write BibTeX entry to file.'
                    )
                    return
        
        commands = [
            ['lualatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', 'main.tex'],
            ['biber', 'main'],
            ['lualatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', 'main.tex'],
            ['lualatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', 'main.tex']
        ]
        self.progress = QtW.QProgressDialog(
            'Generating Poster...', 'Cancel', 0, len(commands), self
        )
        self.progress.setWindowTitle('Generating Poster')
        self.progress.setWindowModality(QtC.Qt.WindowModality.WindowModal)
        self.progress.setAutoClose(True)
        self.progress.setAutoReset(True)
        self.progress.setMinimumDuration(0)
        self.progress.show()
        
        self.thread = LaTeXCompiler(commands)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.compile_finished)
        self.progress.canceled.connect(self.thread.terminate)
        self.thread.start()
    
    def compile_finished(self):
        with open(os.path.join(ROOT, 'latex', 'main.log'), 'r') as f:
            lualatex_log = f.read().strip().splitlines()
            if 'error' in lualatex_log[-1]:
                self.message_dialog(
                    'LaTeX Error',
                    'The following LaTeX error has occured:',
                    [
                        line for line in lualatex_log[:-1] 
                        if lualatex_log[-1].split('==>')[0].strip() in line
                    ][0],
                    '\n'.join(lualatex_log)
                )
                return
        with open(os.path.join(ROOT, 'latex', 'main.blg'), 'r') as f:
            biber_log = f.read().strip().splitlines()
            if 'ERRORS' in biber_log[-1]:
                self.message_dialog(
                    'BibTeX Error',
                    'The following BibTeX error has occured:',
                    [line for line in biber_log[:-1] if 'ERROR' in line][0],
                    '\n'.join(biber_log)
                )
                return
        shutil.copy(os.path.join(ROOT, 'latex', 'main.pdf'), self.save_location.text())
        QtG.QDesktopServices.openUrl(QtC.QUrl.fromLocalFile(self.save_location.text()))
        QtW.QMessageBox.information(self, 'Success', 'Poster generated successfully.')
    
    def closeEvent(self, *args, **kwargs):
        super(QtW.QMainWindow, self).closeEvent(*args, **kwargs)
        for file in os.listdir(os.path.join(ROOT, 'latex')):
            if file not in ['backup', 'fonts', 'lualatex', 'media']:
                os.remove(os.path.join(ROOT, 'latex', file))
        for file in os.listdir(os.path.join(ROOT, 'latex', 'backup')):
            shutil.copy2(
                os.path.join(ROOT, 'latex', 'backup', file), 
                os.path.join(ROOT, 'latex', file)
            )

class LaTeXCompiler(QtC.QThread):
    progress = QtC.pyqtSignal(int)
    finished = QtC.pyqtSignal()
    
    def __init__(self, commands):
        super().__init__()
        self.commands = commands

    def run(self):
        self.progress.emit(0)
        for i, command in enumerate(self.commands):
            process = subprocess.Popen(
                command,
                cwd=os.path.join(ROOT, 'latex'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True, 
                creationflags=CREATE_NO_WINDOW
            )
            stdout, stderr = process.communicate()
            self.progress.emit(i + 1)
        self.finished.emit()

# ----- #

if __name__ == '__main__':
    """
    RCL-UM Journal Club Poster Generator
    Developed by: Affan Adly Nazri
    Version: 2.0

    This is a PyQt6 application that generates posters for the RCL-UM
    Journal Club using LaTeX. It allows users to input presenter and
    meeting details, fetch bibliographic information from a DOI, and 
    compile the poster using LuaLaTeX and Biber.
    """
    ROOT = os.path.abspath(os.path.dirname(__file__))
    CREATE_NO_WINDOW = 0x08000000
    
    app = QtC.QCoreApplication.instance()
    if app is None:
        app = QtW.QApplication(sys.argv)
    window = PosterGenerator()
    window.show()
    app.setStyleSheet(qdarktheme.load_stylesheet())
    app.exec()