/*
 *  SkinProbablilityMaps.h
 *  CurveMatching
 *
 *  Created by roy_shilkrot on 2/8/13.
 *  Copyright (c) 2013 MIT
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 * based on section 2.2.2 of "A survey of skin-color modeling and detection methods", Kukumanu et al 2007
 */

#include "AbstractSkinDetector.h"

class SkinProbablilityMaps : public AbstractSkinDetector<float> {
private:
	MatND skin_hist,non_skin_hist;
	float theta_thresh;
    Scalar hist_bins;
    Scalar low_range;
    Scalar high_range;
    Scalar range_dist;
//				LOOOKIE HERE

	MatND calc_rg_hist(const Mat& img, const Mat& mask, const Scalar& bins = Scalar(250, 250), const Scalar& low = Scalar(0, 0), const Scalar& high = Scalar(1, 1)) {
		Scalar channels(1, 2);
		return this->calc_2D_hist(img,mask,channels,bins,low,high);		
	}
public:
	
	SkinProbablilityMaps():theta_thresh(8.0) {
        hist_bins = Scalar(50,50);
        low_range = Scalar(0.2,0.3);
        high_range = Scalar(0.4,0.5);
        range_dist[0] = high_range[0] - low_range[0];
        range_dist[1] = high_range[1] - low_range[1];
    }
		
	/* simple threshold on HSV and normalized-RGB taken from: 
	 "A survey of skin-color modeling and detection methods", P. Kakumanu, S. Makrogiannis, N. Bourbakis 2006
	 */
	void boostrap(const Mat& rgb, Mat& outputmask) {
		Mat hsv; cvtColor(rgb, hsv, CV_BGR2HSV);
		Mat nrgb = this->getNormalizedRGB(rgb);
		
		Mat mask_hsv, mask_nrgb;
		//H=[0,50], S= [0.20,0.68] and V= [0.35,1.0]
		inRange(hsv, Scalar(0,0.2*255.0,0.35*255.0), Scalar(50.0/2.0,0.68*255.0,1.0*255.0), mask_hsv);
		//r = [0.36,0.465], g = [0.28,0.363]
		inRange(nrgb, Scalar(0,0.28,0.36), Scalar(1.0,0.363,0.465), mask_nrgb);
		
		//rule from "Automatic Feature Construction and a Simple Rule Induction Algorithm for Skin Detection", Gomez & Morales 2002
//		//r/g > 1.185, rb/(r+g+b)^2 > 0.107, rg/(r+g+b)^2 > 0.112
//		inRange(nrgb, Scalar(1.185,0.107,0.112), Scalar::all(1000), mask_nrgb);
		
		if(this->verbose) imshow("mask_hsv",mask_hsv);
		if(this->verbose) imshow("mask_rg", mask_nrgb);
		
		outputmask = mask_hsv & mask_nrgb;
		
		if(this->verbose) imshow("bootstrap", outputmask);
	}
	
	virtual void train(const Mat& img_rgb, const Mat& mask) 
	{
		Mat nrgb = this->getNormalizedRGB(img_rgb);
		
		skin_hist.setTo(0); non_skin_hist.setTo(0);
		skin_hist = calc_rg_hist(nrgb, mask, hist_bins, low_range, high_range);
		non_skin_hist = calc_rg_hist(nrgb,~mask,hist_bins,low_range,high_range);
		
		//create a probabilty density function
		float skin_pixels = countNonZero(mask), non_skin_pixels = countNonZero(~mask);
		for (int ubin=0; ubin < hist_bins[0]; ubin++) {
			for (int vbin = 0; vbin < hist_bins[1]; vbin++) {
				if (skin_hist.at<float>(ubin,vbin) > 0) {
					skin_hist.at<float>(ubin,vbin) /= skin_pixels;
				}
				if (non_skin_hist.at<float>(ubin,vbin) > 0) {
					non_skin_hist.at<float>(ubin,vbin) /= non_skin_pixels;
				}
			}
		}
		
		if(this->verbose) this->visualizeHist(skin_hist,hist_bins,"skin hist");
		if(this->verbose) this->visualizeHist(non_skin_hist,hist_bins,"non skin hist");
		
		this->initialized = true;
	}

	virtual void predict(const Mat& img_rgb, Mat& output_mask) {
		Mat_<Vec3f> nrgb = getNormalizedRGB(img_rgb).reshape(3, img_rgb.rows*img_rgb.cols);
		Mat_<uchar> result_mask(nrgb.size());
		
		for (int i=0; i<nrgb.rows; i++) {
            if (nrgb.at<Vec3f>(i)[1] < low_range[0] || nrgb(i)[1] > high_range[0] ||
                nrgb(i)[2] < low_range[1] || nrgb(i)[2] > high_range[1])
            {
                result_mask(i) = 0;
                continue;
            }
			int gbin = cvRound((nrgb(i)[1] - low_range[0])/range_dist[0] * hist_bins[0]);
			int rbin = cvRound((nrgb(i)[2] - low_range[1])/range_dist[1] * hist_bins[1]);
			float skin_hist_val = skin_hist.at<float>(gbin,rbin);
			if (skin_hist_val > 0) {
				float non_skin_hist_val = non_skin_hist.at<float>(gbin,rbin);
				if (non_skin_hist_val > 0) {
					if((skin_hist_val / non_skin_hist_val) > theta_thresh)
						result_mask(i) = 255;
					else 
						result_mask(i) = 0;
				} else {
					result_mask(i) = 0;
				}
			} else {
				result_mask(i) = 0;
			}
		}
		
		output_mask = result_mask.reshape(1, img_rgb.rows);
	}
	
	void setTheta(float t) { theta_thresh = t; }
};
