/*
 *  EllipticalBoundaryModel.h
 *  CurveMatching
 *
 *  Created by roy_shilkrot on 2/4/13.
 *  Copyright (c) 2013 MIT
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 *  Implementing: "An Elliptical Boundary Model for Skin Color Detection", 
 *	by Jae Y. Lee and Suk I. Yoo (2002)
 *
 *  and "A survey of skin-color modeling and detection methods", 
 *  by P. Kakumanu, S. Makrogiannis, N. Bourbakis (2006)
 */

#include "AbstractSkinDetector.h"

template<typename T>
class EllipticalBoundaryModel : public AbstractSkinDetector<T> {
private:
	Mat_<T> psi;
	Mat_<T> Lambda;
	Matx<T,2,2> Lambda_inv;
	MatND f_hist;
	T theta_thresh;
    Scalar hist_bins;
    Scalar low_range;
    Scalar high_range;
    Scalar range_dist;

		
	void train() {
		T ustep = range_dist[0]/hist_bins[0], vstep = range_dist[1]/hist_bins[1];
		
		//calc n, X_i and mu
		Mat_<T> mu(1,2); mu.setTo(0);
		vector<T> f;
		int n = countNonZero(f_hist);
        int count = 0;
        int N = 0;
		Mat_<T> X(n,2);
		for (T ubin=0; ubin < hist_bins[0]; ubin++) {
			for (T vbin = 0; vbin < hist_bins[1]; vbin++) {
                T histval = f_hist.at<T>(ubin,vbin);
				if (histval > 0) {
					Mat_<T> sampleX = (Mat_<T>(1,2) << low_range[0] + ustep * (ubin+.5), low_range[1] + vstep * (vbin+.5));
                    sampleX.copyTo(X.row(count++));
					f.push_back(histval);
					mu += histval * sampleX;
                    N += histval;
				}
			}
		}
        
		mu /= (T)N;
						
		//calc psi - mean of DB
		reduce(X, psi, 0, CV_REDUCE_AVG);
		
		//calc Lambda
		Lambda.create(2,2);
		for (int i=0; i < n; i++) {
			Mat_<T> X_m_mu = (X.row(i) - mu);
			Mat_<T> prod = f[i] * X_m_mu.t() * X_m_mu;
			Lambda += prod;
		}
		Lambda /= N;
		Mat_<T> linv = Lambda.inv();
		Lambda_inv.val[0] = linv(0,0);
		Lambda_inv.val[1] = linv(0,1);
		Lambda_inv.val[2] = linv(1,0);
		Lambda_inv.val[3] = linv(1,1);
		
		cout << "n = " << n << " N = " << N << " mu " << mu << "\npsi " << psi << "\nlambda_inv "<< Lambda_inv<<"\n";
	}
	
	Mat_<Vec<T, 3> > getCIELuvFromBGR(const Mat& img_rgb) {
		Mat_<Vec<T, 3> > img_rgbf;
		img_rgb.convertTo(img_rgbf, (typeid(T)==typeid(double))?CV_64FC3:CV_32FC3, 1.0/255.0);
		Mat_<Vec<T, 3> > img_cieLuv;
		cvtColor(img_rgbf, img_cieLuv, CV_BGR2Luv);
		return img_cieLuv;
	}		
	
	void assertInput(const Mat& img_rgb, const Mat& mask) {
		assert(img_rgb.size() == mask.size());
		assert(mask.channels() == 1 && mask.type() == CV_8UC1);
		assert(img_rgb.type() == CV_8UC3);
	}	
	
	void getSamplesFromImages(const Mat& img_rgb, 
							  const Mat& mask, 
							  Mat_<Vec<T, 3> >& img_cieLuv,
							  Mat_<T>& samples) {
		assertInput(img_rgb,mask);
		
		Mat maskedrgb(img_rgb.size(),CV_8UC3,Scalar::all(128)); 
		img_rgb.copyTo(maskedrgb, mask);
		imshow("train",maskedrgb);
		
//		img_cieLuv = getCIELuvFromBGR(img_rgb);
        img_cieLuv = this->getNormalizedRGB(img_rgb);
		samples.create(countNonZero(mask),3);
        Mat_<Vec<T, 3> > img_cieLuv_flat = img_cieLuv.reshape(img_cieLuv.channels(), img_cieLuv.rows * img_cieLuv.cols);
        Mat_<uchar> mask_flat = mask.reshape(1,mask.rows*mask.cols);
        int count = 0;
        for (int i=0; i<img_cieLuv_flat.rows; i++) {
            if (mask_flat(i) > 0) {
                samples(count,0) = img_cieLuv_flat(i)[0];
                samples(count,1) = img_cieLuv_flat(i)[1];
                samples(count++,2) = img_cieLuv_flat(i)[2];
            }
        }
	}
	
	MatND calc_uv_hist(const Mat& img, const Mat& mask) {
		Scalar channels(1, 2);
		return this->calc_2D_hist(img,mask,channels,hist_bins,low_range,high_range);
	}
	
public:
	EllipticalBoundaryModel():theta_thresh(1) {
        hist_bins = Scalar(50,50);
        low_range = Scalar(0.2,0.3);
        high_range = Scalar(0.4,0.5);
        range_dist[0] = high_range[0] - low_range[0];
        range_dist[1] = high_range[1] - low_range[1];
    }
	
	void accumTrain(const Mat& img_rgb, const Mat& mask) {
		assert(this->initialized);

		Mat_<Vec<T, 3> > img_cieLuv = this->getNormalizedRGB(img_rgb);
		f_hist += calc_uv_hist(img_cieLuv, mask);
		this->visualizeHist(f_hist,hist_bins,"EBM uv hist");
		
		this->train();
	}
	
	virtual void train(const Mat& img_rgb, const Mat& mask) {
		Mat_<Vec<T, 3> > img_cieLuv = this->getNormalizedRGB(img_rgb);
		f_hist = calc_uv_hist(img_cieLuv,mask);
		this->visualizeHist(f_hist,hist_bins,"EBM uv hist");
		
		this->train();
		
		this->initialized = true;
	}
		
	virtual void predict(const Mat& img_rgb, Mat& output_mask) {
		assert(img_rgb.type() == CV_8UC3);
		if (output_mask.empty()) { output_mask.create(img_rgb.size(), CV_8UC1); }
		output_mask.setTo(0);
		
//		Mat_<Vec<T, 3> > img_cieLuv = getCIELuvFromBGR(img_rgb);
        Mat_<Vec<T, 3> > img_cieLuv = this->getNormalizedRGB(img_rgb);
		Mat_<Vec<T, 3> > img_cieLuv_flat = img_cieLuv.reshape(img_cieLuv.channels(), img_cieLuv.rows * img_cieLuv.cols);
		Mat_<Vec<T, 3> > img_cieLuv_flat_sub = img_cieLuv_flat - Scalar(0,psi(0),psi(1));
		assert(img_cieLuv_flat(0)[1] - psi(0) == img_cieLuv_flat_sub(0)[1]);
		assert(img_cieLuv_flat(0)[2] - psi(1) == img_cieLuv_flat_sub(0)[2]);
		
		Mat_<T> output_mask_Phi(output_mask.rows*output_mask.cols,1);

//		#pragma omp parallel for
		for (int i=0; i<img_cieLuv_flat.rows; i++) {
			//predict per pixel
			Matx<T,1,2> X; X.val[0] = img_cieLuv_flat_sub(i)[1]; X.val[1] = img_cieLuv_flat_sub(i)[2]; //take only u,v
			Matx<T,1,1> prod = X * Lambda_inv * X.t();
			output_mask_Phi(i) = prod(0);
		}
		
		output_mask_Phi = output_mask_Phi.reshape(1, output_mask.rows);
		output_mask = output_mask_Phi < theta_thresh;
	}
	
    void setThetaThresh(T t) { theta_thresh = t; }
};