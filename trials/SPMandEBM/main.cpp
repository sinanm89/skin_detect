#include <string>
#include <vector>
#include <sstream>
#include <map>
#include <set>
#include <fstream>
#include <iostream>
#include <limits>

using namespace std;

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/video/video.hpp>
#include <opencv2/features2d/features2d.hpp>

using namespace cv;

#include "SkinProbablilityMaps.h"
#include "EllipticalBoundaryModel.h"


EllipticalBoundaryModel<float> ebm;
void on_ebm_change(int val, void*) {
    ebm.setThetaThresh((float)val/100.0f);
}

int main(int argc, char** argv)
{

    //	VideoCapture capture("recording_mask1.avi");
    VideoCapture capture(1);
	if (!capture.isOpened()) {
		cerr << "cannot open video\n";
		exit(0);
	}
	SkinProbablilityMaps spm;
    
    namedWindow("ebm");
    int init_theta = 100;
    createTrackbar("theta", "ebm", &init_theta, 200,on_ebm_change);
	Mat mask,ebm_mask,cameraframe;
    
    while (true)
    {
        capture >> cameraframe;
        resize(cameraframe, cameraframe, Size(), 0.5,0.5);
        if (!spm.isInitialized()) {
            spm.boostrap(cameraframe, mask);
        } else {
            spm.predict(cameraframe, mask);
            ebm.predict(cameraframe, ebm_mask);
            medianBlur(ebm_mask, ebm_mask, 3);
            imshow("ebm",ebm_mask);
        }
        medianBlur(mask, mask, 3);
        imshow("tracker", cameraframe);
        imshow("mask", mask);
        int c = waitKey(20);
        if (c=='t') {
            for (int i=0; i<10; i++) { //predict-train 3 times for convergence
                medianBlur(mask, mask, 3);
                spm.train(cameraframe, mask);
                spm.predict(cameraframe, mask);
                imshow("mask", mask);
                waitKey(50);
            }
            ebm.train(cameraframe, mask);
        }
        if(c==' ') {
            imwrite("rgb.png", cameraframe);
            imwrite("mask.png", mask);
        }
        if (c == 'e') {
            ebm.accumTrain(cameraframe, mask);
        }
        if (c==27) {
            exit(0);
        }
    }
     
}
