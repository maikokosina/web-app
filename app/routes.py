# -*- coding: utf-8 -*-

import hashlib
import pymongo
import base64
from flask import render_template, flash, redirect, request
from app import app
from datetime import datetime
from werkzeug.utils import secure_filename
from app.forms import LoginForm, RegistrationForm
from app.forms import AddUser, DeleteUser, BanUser, UnbanUser
from app.forms import AddPage, DeletePage, EditPage, GoToEdit
from app.forms import EditAccess
from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.archive
users = db.users
pages = db.pages
access = db.access
files = db.files

@app.route('/')
@app.route('/home')
def home():

	full_path = '/home/elizaveta/myproject/app/content/home.gif'
	with open(full_path, "rb") as filestring:
		conv = filestring.read()
	data = base64.b64encode(conv)
	data = data.decode("utf-8")
	
	return render_template('home.html', title='Home', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	email = request.form.get('email')
	password = request.form.get('password')
	if request.method == 'POST':
		if form.validate_on_submit():
			passmd5 = hashlib.md5(password.encode('utf-8')).hexdigest()
			if users.find_one({"email": email}) is None:
				flash("Sorry, this user does not exist!")
			else:
				if users.find_one({"password": passmd5.upper()}) is None:
					flash("Wrong password!")
				else:
					check_status = 0
					for sttype in users.find({"email": email}):
						check_status = sttype['account_status']
					if check_status == 4:
						flash ("Sorry, but your account is banned. Try another account.")
					else:
						flash("Success!")
						users.update_one({
							"email": email},{
							'$set':{"last_visit": datetime.now().timestamp(),
							"account_status": 1,
							"is_active": True}
							}, upsert = False)
						
						global idname
						for findid in users.find({"email": email}):
							idname = findid['user_id']
							
						return redirect('profile')
	return render_template('login.html', title='Sign In', form=form)
	
@app.route('/registration', methods=['GET', 'POST'])
def registration():
	form = RegistrationForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			email = request.form.get('email')
			if users.find_one({"email": email}) is None:
				password = request.form.get('password')
				confirm_password = request.form.get('confirm_password')
				if password != confirm_password:
					flash("Sorry, passwords don't match!")
				else:
					last_id = 0
					for lid in users.find().sort("user_id", pymongo.DESCENDING).limit(1):
						last_id = lid['user_id']
					
					last_id = last_id + 1
					user_name = request.form.get('user_name')
					hashpassmd5 = hashlib.md5(password.encode('utf-8')).hexdigest().upper()
					doc = { "user_id": last_id,
						"user_name": user_name,
						"password": hashpassmd5,
						"email": email,
						"account_status": 1,
						"account_type": 3,
						"is_active": True,
						"signup_time": datetime.now().timestamp(),
						"last_visit": datetime.now().timestamp(),
						"avatar": bytes.fromhex(' ')}
					insert_doc = users.insert_one(doc)
					flash("Registration success!")
					return redirect('login')
			else:
				flash("Sorry, the user with this email is already registered!")
	return render_template('registration.html', title='Registration', form=form)

@app.route('/mongousers', methods=['GET', 'POST'])
def mongousers():

	form1 = AddUser()
	form2 = DeleteUser()
	form3 = BanUser()
	form4 = UnbanUser()
	all_users = users.find()
	avatars1 = []
	signup1 = []
	last1 = []

	for user in users.find():
		
		checkdateid = int(user["user_id"])
		checkstatus = int(user["account_status"])
		signup = datetime.utcfromtimestamp(user["signup_time"]).strftime('%Y-%m-%d %H:%M:%S')
		signup1.append(signup)
		
		last = datetime.utcfromtimestamp(user["last_visit"]).strftime('%Y-%m-%d %H:%M:%S')
		last1.append(last)
		
		checkdate1 = datetime.now()
		checkdate2 = datetime.strptime(last, '%Y-%m-%d %H:%M:%S')
		diff = abs((checkdate2-checkdate1).days)
		
		if checkstatus != 4:
			if (diff < 8):
				users.update_one({
					"user_id": checkdateid},{
					'$set':{"account_status": 1}
						}, upsert = False)
			if (diff > 7) and (diff < 31):
				users.update_one({
					"user_id": checkdateid},{
					'$set':{"account_status": 2}
						}, upsert = False)
			if diff > 30:
				users.update_one({
					"user_id": checkdateid},{
					'$set':{"account_status": 3}
						}, upsert = False)
		
		avatar = user["avatar"]
		avatar = base64.b64encode(avatar)
		avatar = avatar.decode("utf-8")
		avatars1.append(avatar)
		
	if request.method == 'POST':
		if form1.validate_on_submit():
			email1 = request.form.get('email1')
			if users.find_one({"email": email1}) is None:
				last_id = 0
				for lid in users.find().sort("user_id", pymongo.DESCENDING).limit(1):
					last_id = lid['user_id']
					
				last_id = last_id + 1
				user_name = request.form.get('user_name')
				password = request.form.get('password')
				account_type = request.form.get('account_type')
				hashpassmd5 = hashlib.md5(password.encode('utf-8')).hexdigest().upper()
				doc = { "user_id": last_id,
					"user_name": user_name,
					"password": hashpassmd5,
					"email": email1,
					"account_status": 3,
					"account_type": int(account_type),
					"is_active": False,
					"signup_time": datetime.now().timestamp(),
					"last_visit": 0,
					"avatar": bytes.fromhex(' ')}
				insert_doc = users.insert_one(doc)
				flash("User added!")
				return redirect('mongousers')
			else:
				flash("Sorry, the user with this email is already registered!")
		if form2.validate_on_submit():
			email2 = request.form.get('email2')		
			if users.find_one({"email": email2}) is None:
				flash("Sorry, there is no user with this email!")
			else:
				users.delete_one({"email": email2})
				flash("User deleted.")
				return redirect('mongousers')
		
		if form3.validate_on_submit():
			email3 = request.form.get('email3')		
			if users.find_one({"email": email3}) is None:
				flash("Sorry, there is no user with this email!")
			else:
				users.update_one({
							"email": email3},{
							'$set':{
							"account_status": 4,
							"is_active": False}
							}, upsert = False)
				flash("User banned.")
				return redirect('mongousers')
				
		if form4.validate_on_submit():
			email4 = request.form.get('email4')		
			if users.find_one({"email": email4}) is None:
				flash("Sorry, there is no user with this email!")
			else:
				users.update_one({
							"email": email4},{
							'$set':{
							"account_status": 3,
							"is_active": True}
							}, upsert = False)
				flash("User unbanned.")
				return redirect('mongousers')
	
	return render_template('mongousers.html', title='Users', all_users=all_users, avatars1=avatars1, signup1=signup1, last1=last1, form1=form1, form2=form2, form3=form3, form4=form4)

@app.route('/mongopages', methods=['GET', 'POST'])
def mongopages():
	
	form1 = AddPage()
	form2 = DeletePage()
	
	all_pages = pages.find()
	arrayfiles = []
	
	for acctype in users.find({"user_id": idname}):
		check_type = acctype['account_type']
		
	for page in pages.find():
		files1 = page["files"]
		arrfiles = [int(fileid) for fileid in files1]
		arrfiles1 = ''
		for afile in files.find({"file_id": {"$in": arrfiles}}):
			arrfile = afile['filename']
			arrfiles1 = arrfiles1 + arrfile + ', '
		arrfiles2 = arrfiles1[:-2]
		arrayfiles.append(arrfiles2)
	
	if request.method == 'POST':
		if form1.validate_on_submit():
			title = request.form.get('addtitle')
			if pages.find_one({"title": title}) is None:
				last_id = 0
				for lid in pages.find().sort("page_id", pymongo.DESCENDING).limit(1):
					last_id = lid['page_id']
					
				last_id = last_id + 1
				
				owner_id = request.form.get('addowner_id')
				owner_id = int(owner_id)
				tag = request.form.get('addtag')
				description = request.form.get('adddescription')
				keywords = request.form.get('addkeywords')
				body = request.form.get('addbody')
				doc = { "page_id": last_id,
					"owner_id": owner_id,
					"tag": tag,
					"title": title,
					"description": description,
					"keywords": keywords,
					"body": body,
					"files": []}
				insert_doc = pages.insert_one(doc)
				
				for lacl in access.find().sort("acl_id", pymongo.DESCENDING).limit(1):
					last_acl = lacl['acl_id']
					
				readacc = access.insert_one({
					"acl_id": last_acl+1,
					"page_id": last_id, 
					"privilege": 'Read',
					"list": [owner_id]})
				
				writeacc = access.insert_one({
					"acl_id": last_acl+2,
					"page_id": last_id, 
					"privilege": 'Write',
					"list": [owner_id]})
				
				flash("Page added!")
				return redirect('mongopages')
			else:
				flash("Sorry, the page with this title is already exists!")
	
		if form2.validate_on_submit():
			page_id_del = request.form.get('page_id_del')
			page_id_del = int(page_id_del)		
			if pages.find_one({"page_id": page_id_del}) is None:
				flash("Sorry, there is no page with this ID!")
			else:
				pages.delete_one({"page_id": page_id_del})
				access.delete_many({"page_id": page_id_del})
				flash("Page deleted.")
				return redirect('mongopages')
		
	return render_template('mongopages.html', title='Pages', check_type=check_type, all_pages=all_pages, arrayfiles=arrayfiles, form1=form1, form2=form2)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
	
	for acctype in users.find({"user_id": idname}):
		check_type = acctype['account_type']
		
	for findname in users.find({"user_id": idname}):
		name = findname['user_name']
		
	for avat in users.find({"user_id": idname}):
		avatar = avat["avatar"]
		avatar = base64.b64encode(avatar)
		avatar = avatar.decode("utf-8")
	
	return render_template('profile.html', title='Profile', idname=idname, name=name, check_type=check_type, avatar=avatar)


@app.post('/profile/editavatar')
def editavatar():
	
	image = request.files["nameavatar"]
	filename = secure_filename(image.filename)
	
	if filename != '':
		full_path = '/home/elizaveta/myproject/app/content/' + filename

		with open(full_path, "rb") as avatarstring:
			conv = avatarstring.read()
			users.update_one({
				"user_id": idname},{
				'$set':{
				"avatar": conv}
				}, upsert = False)
		flash("Avatar changed!")
		return redirect('/profile')
	else:
		flash("No file selected!")
		return redirect('/profile')
		
@app.post('/profile/deleteavatar')
def deleteavatar():
	
	users.update_one({
		"user_id": idname},{
		'$set':{
		"avatar": bytes.fromhex(' ')}
		}, upsert = False)
	
	flash("Avatar deleted!")
	return redirect('/profile')
	
@app.route('/data', methods=['GET', 'POST'])
def data():
	return render_template('data.html', title='Data')
	
@app.route('/mongopages/<title>', methods=['GET', 'POST'])
def page(title):
	
	form = GoToEdit()
	owner_name = ''
	arrayfiles = []
	pagedata = pages.find({"title": title})
	
	
	for page in pages.find({"title": title}):
		owner_id = page['owner_id']
		files1 = page["files"]
		arrfiles = [int(fileid) for fileid in files1]
	
	for afile in files.find({"file_id": {"$in": arrfiles}}):
		arrfile = afile['filename']
		arrayfiles.append(arrfile)

		
	pageowner = int(owner_id)
	for uowner in users.find({"user_id": pageowner}):
		owner_name = uowner['user_name']
	
	if request.method == 'POST':
		if form.validate_on_submit():
			url = '/mongopages/' + title + '/edit'
			return redirect(url)
				
	return render_template('title.html', title=title, form=form, pagedata=pagedata, owner_name=owner_name, arrayfiles=arrayfiles)
	
@app.route('/mongopages/<title>/<filename>', methods=['GET', 'POST'])
def datafile(title, filename):
	
	part1, part2 = filename.split('.')
	lines = []	
	
	for filedata in files.find({"filename": filename}):
		data = filedata["file"]
		
		if part2 == 'txt':
			data = data.decode("utf-8")
			lines = data.split('\n')
		else:
			data = base64.b64encode(data)
			data = data.decode("utf-8")
	
	return render_template('file.html', title=title, filename=filename, data=data, part1=part1, part2=part2, lines=lines)
	
@app.route('/mongopages/<title>/edit', methods=['GET', 'POST'])
def edit(title):
	
	form1 = EditPage()
	arrayfiles = []
	
	for acctype in users.find({"user_id": idname}):
		check_type = acctype['account_type']
	
	for page in pages.find({"title": title}):
		idpage = page['page_id']
		edit_tag = page['tag']
		edit_description = page['description']
		edit_keywords = page['keywords']
		edit_body = page['body']
		arrfile = page['files']
		arrfiles = [int(fileid) for fileid in arrfile]
	
	for afile in files.find({"file_id": {"$in": arrfiles}}):
		data = afile['filename']
		arrayfiles.append(data)
	
	form1.edittag.data = edit_tag
	form1.editdescription.data = edit_description
	form1.editkeywords.data = edit_keywords
	form1.editbody.data = edit_body
	
	readaccess = access.find({"page_id": idpage, "privilege": 'Read'})
	writeaccess = access.find({"page_id": idpage, "privilege": 'Write'})	
	
	return render_template('edit.html', title=title, form1=form1, readaccess=readaccess, writeaccess=writeaccess, idname=idname, check_type=check_type, arrayfiles=arrayfiles)
	
@app.post('/mongopages/<title>/edit/editpage')
def editpage(title):
	
	edittag = request.form.get('edittag')
	editdescription = request.form.get('editdescription')
	editkeywords = request.form.get('editkeywords')
	editbody = request.form.get('editbody')
					
	pages.update_one({
		"title": title},{
		'$set':{"tag": edittag,
		"description": editdescription,
		"keywords": editkeywords,
		"body": editbody}
		}, upsert = False)
				
	flash("Page edited!")
			
	url = '/mongopages/' + title + '/edit'
	return redirect(url)

@app.post('/mongopages/<title>/deletefile/<filename>')
def deletefile(title, filename):
	
	arrfiles = []
	
	for arrfile in pages.find({"title": title}):
		array = arrfile['files']
	
	arrfiles = [int(fileid1) for fileid1 in array]
	
	for  idfile in files.find({"filename": filename}):
		fileid = idfile['file_id']
		fileid= int(fileid)
		
	arrfiles.remove(fileid)
	
	pages.update_one({
			"title": title},{
			'$set':{"files": arrfiles}
					}, upsert = False)
	
	files.delete_one({"file_id": fileid})
	
	flash("File deleted.")
	url = '/mongopages/' + title + '/edit'
	return redirect(url)
	
@app.post('/mongopages/<title>/edit/addfile')
def addfile(title):
	
	arrayfiles = []
	checkarr = []
	
	for page in pages.find({"title": title}):
		arrfile = page['files']
		arrfiles = [int(fileid) for fileid in arrfile]
						
	for page in pages.find({"title": title}):
		idpage = page["page_id"]
		checkarr = page["files"]
		
	for afile in files.find({"file_id": {"$in": arrfiles}}):
		data = afile['filename']
		arrayfiles.append(data)
		
	idpage = idpage * 10
	idpage1 = idpage + 10
			
	if checkarr == []:
		last_file = idpage
	else:
		for lfile in files.find({"file_id": {"$gt": idpage, "$lt": idpage1}}).sort("file_id", pymongo.DESCENDING).limit(1):
			last_file = lfile['file_id']		
	last_file = last_file + 1
			
	files1 = request.files["editfiles"]
	filename = secure_filename(files1.filename)
	full_path = '/home/elizaveta/myproject/app/content/' + filename

	if filename !=  '':
		if filename not in arrayfiles:
			with open(full_path, "rb") as filestring:
				conv = filestring.read()
				
			files.insert_one({
				"file_id": last_file,
				"file": conv, 
				"filename": filename})
				
			arrfiles.append(last_file)
					
			pages.update_one({
				"title": title},{
				'$set':{"files": arrfiles}
					}, upsert = False)
				
			flash("File added!")
		else: 
			flash('This file is already on page!')
	else:
		flash("No file selected!")
			
	url = '/mongopages/' + title + '/edit'
	return redirect(url)
	
@app.route('/mongopages/<title>/edit/access', methods=['GET', 'POST'])
def editaccess(title):
	
	form = EditAccess()
	usid = []
	cnt = 0
	
	for ids in users.find():
		us = int(ids['user_id'])
		usid.append(us)
	 
	form.editlist.choices = usid
	 
	for page in pages.find({"title": title}):
		idpage = page['page_id']
	
	if request.method == 'POST':
		if form.validate_on_submit():
			editlist = request.form.getlist('editlist')
			edlist = [int(idus) for idus in editlist]
			typeofprivilege = request.form.get('typeofprivilege')
			access.update_one({
					"page_id": idpage, "privilege": typeofprivilege},{
					'$set':{"list": edlist}
							}, upsert = False)
			
			flash("Access edited!")
			url = '/mongopages/' + title + '/edit'
			return redirect(url)
	
	return render_template('access.html', title=title, form=form, idpage=idpage)
