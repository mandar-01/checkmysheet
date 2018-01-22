from django.shortcuts import render
from django.http import HttpResponse
from .forms import PostForm
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import pprint as pp
from checkmysheet import settings
def create(request):
	form = PostForm(request.POST or None,request.FILES or None)
	context = {'form':form,'status':'not working'}
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		context['status'] = 'working'
		process(settings.MEDIA_ROOT + "\\" + request.FILES['image'].name)
		return render(request,"create.html",context)
	return render(request,"create.html",context)

# def upload_file(request):
# 	context = {'status':'not working'}
# 	#print request.FILES['myfile']
# 	if request.method == 'POST':
# 	    form = UploadFileForm(request.POST, request.FILES)
# 	    if form.is_valid():
# 	    	context['status'] = 'working'
# 	    	print request.FILES['image'].name
# 	    	pretty = pp.PrettyPrinter(indent=4)
# 	    	#print pretty.pprint(form.cleaned_data(request.FILES['image']))
# 	    	#process(request.FILES[u'image'])
# 	    	process(request.FILES['image'].name)
# 	    	return render(request,'create.html',context)
# 	else:
# 	    form = UploadFileForm()
# 	return render(request, 'create.html', {'form': form})


# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
# 	help="path to the input image")
# args = vars(ap.parse_args())


def auto_canny(image, sigma=0.33):
	v = np.median(image)
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	return edged

def process(path):

	ANSWER_KEY = {0: 0, 1: 1, 2: 1, 3: 2, 4: 0, 5: 0, 6: 3, 7: 2, 8: 1, 9: 0, 10: 0, 11: 3, 12: 0, 13: 2, 14: 3}
	image = cv2.imread(path)
	#image = img
	r = 500.0 / image.shape[1]
	dim = (500, int(image.shape[0] * r))
	 
	image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (9, 9), 0)
	edged = cv2.Canny(blurred, 75, 200)

	cv2.imshow('edged', edged)
	cv2.waitKey(0)
	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	docCnt = None

	if len(cnts) > 0:
		cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
		for c in cnts:
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.02 * peri, True)
			if len(approx) == 4:
				docCnt = approx
				break
	paper = four_point_transform(image, docCnt.reshape(4, 2))
	warped = four_point_transform(gray, docCnt.reshape(4, 2))
	thresh = cv2.threshold(warped, 0, 255,
		cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

	cv2.imshow('edged', thresh)
	cv2.waitKey(0)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	questionCnts = []

	for c in cnts:
		(x, y, w, h) = cv2.boundingRect(c)
		ar = w / float(h)
		if w >= 12 and h >= 12 and ar >= 0.9 and ar <= 1.1:
			questionCnts.append(c)

	questionCnts = contours.sort_contours(questionCnts,
		method="top-to-bottom")[0]
	correct = 0

	cv2.drawContours(paper, questionCnts, -1, 255, 2)
	cv2.imshow('image', paper)
	cv2.waitKey(0)
	for (q, i) in enumerate(np.arange(0, len(questionCnts), 4)):
		cnts = contours.sort_contours(questionCnts[i:i + 4])[0]
		bubbled = None
		for (j, c) in enumerate(cnts):
			mask = np.zeros(thresh.shape, dtype="uint8")
			cv2.drawContours(mask, [c], -1, 255, -1)
			mask = cv2.bitwise_and(thresh, thresh, mask=mask)
			total = cv2.countNonZero(mask)
			if bubbled is None or total > bubbled[0]:
				bubbled = (total, j)
		color = (0, 0, 255)
		k = ANSWER_KEY[q]

		if k == bubbled[1]:
			color = (0, 255, 0)
			correct += 1
		cv2.drawContours(paper, [cnts[k]], -1, color, 3)

	# grab the test taker
	score = (correct / 4.0) * 100
	print("[INFO] score: {:.2f}%".format(score))
	cv2.putText(paper, "{:.2f}%".format(score), (10, 30),
		cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
	cv2.imshow("Original", image)
	cv2.imshow("Exam", paper)
	cv2.waitKey(0)