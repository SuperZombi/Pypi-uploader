import sys
import os
import shutil
from time import sleep
import json
from tkinter.filedialog import askopenfilename, asksaveasfilename

this_require = ["FreeSimpleGUI", "setuptools", "twine", "wheel"]
os.system(f'pip install --upgrade {" ".join(this_require)}')

import FreeSimpleGUI as sg
import setuptools
import twine
import wheel


def infinite(start=0):
	while True:
		yield start
		start += 1

def load_project(window, filename):
	with open(filename, 'r', encoding='utf-8') as file:
		data = json.load(file)
	for key, value in data.items():
		if key in window.AllKeysDict:
			window[key].update(value)
		else:
			if key == "dependencies":
				add_dependencies(window, value)

def save_project(filename, data):
	allowed_keys = ['folder', 'package_name', 'version', 'description', 'readme', 'username', 'email', 'github', 'docs', 'python_ver']
	final = {key: value for key, value in data.items() if key in allowed_keys and value}

	dependencies = {value for key, value in data.items() if isinstance(key, tuple) and 'dependency' in key[0] and value}
	if len(dependencies) > 0:
		final["dependencies"] = list(dependencies)

	with open(filename, 'w', encoding='utf-8') as file:
		file.write(json.dumps(final, indent=4))


sg.theme('DarkAmber')
window_title = "Pypi uploader"

main = [[sg.T("Select project folder: ", font='16'), sg.FolderBrowse("Browse", target='folder', font='12')],
		[sg.Input("", size=(40,1), key="folder", enable_events=True)],
		[sg.T("Important!\nThis folder should contain the __init__.py file!\n", text_color="red", font='Courier 12')],
		[sg.T("Load to:", font='16')],
		[sg.Radio("Pypi", 0, default=False, key="pypi", font='Segoe 12'), sg.Radio("Test Pypi", 0, default=True, key="test_pypi", font='Segoe 12')],[sg.T("")],
		[sg.T("Package name: ", font='12'), sg.Input("", size=(26,1), key="package_name")],
		[sg.T("Version:            ", font='12'), sg.Input("", size=(15,1), key="version")],
		[sg.T("Description:       ", font='12'), sg.Input("", size=(26,1), key="description")],[sg.T("")],
		[sg.T("Select README.md file: ", font='12')],
		[sg.Input("", size=(37,1), key="readme"), sg.FileBrowse("Browse", file_types=(("Markdown File", "*.md"),), target='readme', font='12'), sg.T("(Optional)", text_color="yellow", font='Arial 12')],[sg.T("")],
		[sg.T("Your username:   ", font='12'), sg.Input("", size=(26,1), key="username")],
		[sg.T("Your password:   ", font='12', key="password_text"), sg.Input("", size=(26,1), key="password", password_char='*'), sg.B("Show", key="show-hide")],
		[sg.Checkbox("token", font='12', key="token", enable_events=True)],
		[sg.T("Your email:          ", font='12'), sg.Input("", size=(26,1), key="email")],
		[sg.T("Github repository: ", font='12'), sg.Input("", size=(26,1), key="github"), sg.T("(Optional)", text_color="yellow", font='Arial 12')],
		[sg.T("Documentation:    ", font='12'), sg.Input("", size=(26,1), key="docs"), sg.T("(Optional)", text_color="yellow", font='Arial 12')],[sg.T("")],
		[sg.T("Required Dependencies: ", font='12'), sg.Button(' + ', key="add_dependency")],
		[sg.Col([], scrollable=True, vertical_scroll_only=True, size=(500, 0), key='-dependencies-')],[sg.T("")],
		[sg.T("Python version: ", font='12'), sg.Input('{0[0]}.{0[1]}'.format(sys.version_info), size=(10,1), key="python_ver")],
		[sg.T("Delete all created files, folders and archives after upload?", font='Segoe 14')],
		[sg.Radio("Yes", 2, default=False, key="delete_yes", font='Segoe 12'), sg.Radio("No", 2, default=True, key="delete_no", font='Segoe 12')],
		[sg.Push(), sg.OK("Upload", font='12'), sg.Push()]]


layout = [
	[sg.Menu([['Project', ['Import', 'Export']], ['Requirements', ['Select file::requirements']]], text_color=sg.theme_text_color(), background_color=sg.theme_background_color())],
	[sg.Column(main, size=(500,600), scrollable=True, vertical_scroll_only=True, key="__main__")]
]

window = sg.Window(window_title, layout, finalize=True)

def button_pointer():
	[el.set_cursor("hand2") for el in window.element_list() if isinstance(el, sg.Button)]

def update_window_height(root, scrollzone):
	scrollzone.contents_changed()
	scrollzone.Widget.pack_propagate(0)
	new_height = scrollzone.TKColFrame.TKFrame.winfo_reqheight()
	scrollzone.set_size((495, min(180, new_height)))
	scrollzone.widget.canvas.yview_moveto(1)
	
	window_height = root.TKColFrame.TKFrame.winfo_reqheight()
	root.set_size((500, window_height))

def add_dependencies(window, array=None):
	if not array: array = [""]
	for value in array:
		item_num = next(dep_index)
		window.extend_layout(window['-dependencies-'],[[sg.pin(
			sg.Col([[sg.B(sg.SYMBOL_X, k=('remove_dependency', item_num), border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color())),
					 sg.Input(value, size=(37,1), k=('dependency', item_num)),
			]], k=('dependency_item', item_num)))
		]])
	window.refresh()
	update_window_height(window['__main__'], window['-dependencies-'])
	button_pointer()

def load_requirements(window, file):
	with open(file, 'r') as f:
		requires = map(lambda x: x.strip(), f.readlines())
		add_dependencies(window, requires)

button_pointer()
dep_index = infinite(1)
showing = False
if os.path.exists("requirements.txt"): load_requirements(window, "requirements.txt")

while True:
	event, values = window.read()

	if event == sg.WIN_CLOSED:
		sys.exit()

	if event == "show-hide":
		showing = not showing
		if showing == True:
			window['password'].update(password_char='')
			window["show-hide"].update("Hide")
		else:
			window['password'].update(password_char="*")
			window["show-hide"].update("Show")

	elif event == "token":
		if values["token"]:
			window["password_text"].update("Your API token:   ")
		else:
			window["password_text"].update("Your password:   ")

	elif event == "folder":
		req_file = os.path.join(values["folder"], "requirements.txt")
		if os.path.exists(req_file):
			load_requirements(window, req_file)

	elif event == "Select file::requirements":
		file = askopenfilename(filetypes=[("Requirements", "*.txt"), ("All files", "*.*")])
		if file: load_requirements(window, file)

	elif event == "add_dependency":
		add_dependencies(window)
	
	elif event[0] == 'remove_dependency':
		window[('dependency_item', event[1])].update(visible=False)
		window.refresh()
		update_window_height(window['__main__'], window['-dependencies-'])


	if event == "Upload":
		break
	elif event == "Import":
		file = askopenfilename(filetypes=[("Project config", "*.build *.config *.json"), ("All files", "*.*")])
		if file: load_project(window, file)

	elif event == "Export":
		file = asksaveasfilename(defaultextension='.build', filetypes=[(".build", ".build"), (".config", ".config"), (".json", ".json")])
		if file: save_project(file, values)

upload_to_pypi = values["pypi"]
upload_to_test_pypi = values["test_pypi"]
username = values["username"]
password = values["password"]
userlogin = "__token__" if values["token"] else values["username"]
dependencies = {value.strip() for key, value in values.items() if isinstance(key, tuple) and 'dependency' in key[0] and value.strip()}

delete_temp_files = False
if values["delete_yes"] == True:
	delete_temp_files = True
package_name = values["package_name"]
path = values["folder"].split("/")
folder = ""
for i in range (len(path)-1):
	folder += path[i]
	
	if i == len(path)-1:
		break
	folder += "/"

comand = "import setuptools\n"
if values["readme"] != "":
	with open(values["readme"], 'r', encoding='utf-8') as fh:
		long_description = fh.read()
	with open('README.md', 'w', encoding='utf-8') as fh:
		fh.write(long_description)
	comand += "with open('README.md', 'r', encoding='utf-8') as fh:\n"
	comand += "	long_description = fh.read()\n"

comand += "\n"
comand += "setuptools.setup(\n"
comand += "	name='" + str(values["package_name"]) + "',\n"
comand += "	version='" + str(values["version"]) + "',\n"
comand += "	author='" + str(values["username"]) + "',\n"
comand += "	author_email='" + str(values["email"]) + "',\n"
comand += "	description='" + str(values["description"]) + "',\n"

if values["readme"] != "":
	comand += "	long_description=long_description,\n"
	comand += "	long_description_content_type='text/markdown',\n"

if values["github"] != "":
	comand += "	url='" + str(values["github"]) + "',\n"

if values["docs"] != "":
	comand += "	project_urls={\n		'Documentation': '" + str(values["docs"]) + "',\n	},\n"

comand += "	packages=['" + str(path[len(path)-1]) + "'],\n"

if len(dependencies) > 0:
	comand += "	install_requires=["
	comand += ', '.join(f'"{item}"' for item in dependencies)
	comand += "],\n"

comand += "	include_package_data=True,\n"
comand += '	classifiers=[\n		"Programming Language :: Python :: 3",\n		"License :: OSI Approved :: MIT License",\n		"Operating System :: OS Independent",\n	],\n'

if values["python_ver"] != "":
	comand += "	python_requires='>="+str(values["python_ver"])+"',\n"
else:
	comand += "	python_requires='>=3.6',\n"
comand += ")"


window.close()

layout = [[sg.T("Generating setup files...", key="text")],[sg.T("")]]
window = sg.Window(window_title, layout)    
event, values = window.read(timeout = 10)
sleep(1)


with open(str(folder) + "setup.py", 'w', encoding='utf-8') as file:
	file.write(comand)

with open(str(folder) + "setup.cfg", 'w') as file:
	file.write("[egg_info]\ntag_build = \ntag_date = 0")

with open(str(folder) + "MANIFEST.in", 'w') as file:
	file.write(f"recursive-include {path[len(path)-1]} *")


window['text'].update("Generating distribution archives...")
window.Refresh()

os.system("python setup.py sdist bdist_wheel")
sleep(1)

window['text'].update("Uploading files...")
window.Refresh()


if upload_to_pypi:
	result = os.system("python -m twine upload dist/* -u " + str(userlogin) + " -p " + str(password))
else:
	result = os.system("python -m twine upload --repository testpypi dist/* -u " + str(userlogin) + " -p " + str(password))

if delete_temp_files:
	window['text'].update("Removing temporary files...")
	window.Refresh()

	shutil.rmtree('build')
	shutil.rmtree("dist")
	os.remove(str(folder) + "setup.cfg")
	os.remove(str(folder) + "setup.py")
	os.remove(str(folder) + "MANIFEST.in")
	shutil.rmtree(str(package_name) + ".egg-info")

if result == 0:
	window['text'].update("Uploaded successfully!")
else:
	window['text'].update("An error occurred!", text_color="red")

window.Refresh()
while True:
	event, values = window.read()
	if event == sg.WIN_CLOSED:
		sys.exit()
