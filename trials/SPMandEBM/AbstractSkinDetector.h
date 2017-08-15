/*
 *  AsbtractSkinDetector.h
 *  CurveMatching
 *
 *  Created by roy_shilkrot on 2/9/13.
 *  Copyright (c) 2013 MIT
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 */
#pragma once
#include "AbstractAlgorithm.h"

template<int w, int h>
void imshow_(const char* winname, const Mat& img) {
    Mat resized; resize(img, resized, Size(w,h));
    imshow(winname,resized);
}

template<typename T>
class AbstractSkinDetector : public AbstractAlgorithm {
protected:

	void visualizeHist(MatND& hist,Scalar bins, const char* histwinname) {
		Mat histImg = Mat::zeros(bins[0], bins[1], CV_8UC3);
		double maxVal=0;
		minMaxLoc(hist, 0, &maxVal, 0, 0);
		cout << "hist maxVal " << maxVal << "\n";
		
		for (int ubin=0; ubin < bins[0]; ubin++) {
			for (int vbin = 0; vbin < bins[1]; vbin++) {
				float binVal = hist.at<T>(ubin, vbin);
				int intensity = cvRound(binVal*255/maxVal);
				rectangle( histImg, Point(ubin, vbin),
						  Point(ubin+1,vbin+1),
						  Scalar(intensity,255,180),
						  CV_FILLED );
			}
		}
		
		cvtColor(histImg, histImg, CV_HSV2BGR);
		imshow_<250,250>(histwinname, histImg );
	}		
	
	MatND calc_2D_hist(const Mat& img, const Mat& mask, Scalar wchannels, Scalar bins, Scalar low, Scalar high) {
		MatND hist;
		int histSize[] = { bins[0], bins[1] };
		T uranges[] = { low[0], high[0] };
		T vranges[] = { low[1], high[1] };
		const T* ranges[] = { uranges, vranges };
		int channels[] = {wchannels[0], wchannels[1]};
		
		calcHist( &img, 1, channels, mask,
				 hist, 2, histSize, ranges,
				 true, // the histogram is uniform
				 false );
				
		return hist;
	}
    
    Mat getNormalizedRGB(const Mat& rgb) {
		assert(rgb.type() == CV_8UC3);
		Mat rgb32f;
		rgb.convertTo(rgb32f, CV_32FC3);
		
		vector<Mat> split_rgb;
		split(rgb32f, split_rgb);
		Mat sum_rgb = split_rgb[0] + split_rgb[1] + split_rgb[2];
		split_rgb[0].setTo(0); //split_rgb[0] / sum_rgb;
		split_rgb[1] = split_rgb[1] / sum_rgb;
		split_rgb[2] = split_rgb[2] / sum_rgb;
        //		sum_rgb = sum_rgb.mul(sum_rgb);
        //		split_rgb[0] = split_rgb[2] / split_rgb[1];
        //		split_rgb[1] = split_rgb[2].mul(split_rgb[0]) / sum_rgb;
        //		split_rgb[2] = split_rgb[2].mul(split_rgb[1]) / sum_rgb;
		
		merge(split_rgb,rgb32f);
		if(this->verbose) imshow("normalized rgb", rgb32f);
		return rgb32f;
	}

    
	
public:
    AbstractSkinDetector():verbose(false) {}
    bool verbose;

	virtual void train(const Mat& img_rgb, const Mat& mask) = 0;
	virtual void predict(const Mat& img_rgb, Mat& output_mask) = 0;

};