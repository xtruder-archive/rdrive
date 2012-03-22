/*
 * Copyright 2011 - Churn Labs, LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.churnlabs.ffmpegsample;

import android.app.Activity;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ImageView;

public class MainActivity extends Activity implements Runnable {
	private static native void openFile();
	private static native void drawFrame(Bitmap bitmap);
	private static native void drawFrameAt(Bitmap bitmap, int secs);
	
	private Bitmap mBitmap;
	private int mSecs = 0;
	
	private Thread working_thread;
	
	private ImageView i;
	
    static {
    	System.loadLibrary("ffmpegutils");
    }
    
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //setContentView(new VideoView(this));
        setContentView(R.layout.main);
        
        working_thread= new Thread(this);
        openFile();
        
        i = (ImageView)findViewById(R.id.frame);
        
        Button btn = (Button)findViewById(R.id.frame_adv);
        btn.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				working_thread.start();
			}
		});
        
       /* Button btn_fwd = (Button)findViewById(R.id.frame_fwd);
        btn_fwd.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				mSecs += 5;
				drawFrameAt(mBitmap, mSecs);
				ImageView i = (ImageView)findViewById(R.id.frame);
				i.setImageBitmap(mBitmap);
			}
		});
        
        Button btn_back = (Button)findViewById(R.id.frame_back);
        btn_back.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				mSecs -= 5;
				drawFrameAt(mBitmap, mSecs);
				ImageView i = (ImageView)findViewById(R.id.frame);
				i.setImageBitmap(mBitmap);
			}
		});*/
    }
    
    public void run()
    {
    	final Bitmap decodec_frame= Bitmap.createBitmap(320, 240, Bitmap.Config.ARGB_8888);
    	while(true)
    	{
    		drawFrame(decodec_frame);
            i.post(new Runnable() {
            public void run() {
                    i.setImageBitmap(decodec_frame);
            }});
    	}
    }
}