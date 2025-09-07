/*
Copyright (c) 2011-2013, Lorenzo Gomez (lorenzobgomez@gmail.com)
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of 
conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list 
of conditions and the following disclaimer in the documentation and/or other materials 
provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED 
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>

struct input_event {
    struct timeval time;
    unsigned short type;
    unsigned short code;
    unsigned long value;
};


void goSleep(uint64_t nsec)
{
    struct timespec timeout0;
    struct timespec timeout1;
    struct timespec* tmp;
    struct timespec* t0 = &timeout0;
    struct timespec* t1 = &timeout1;

    t0->tv_sec = (long)(nsec / 1000000000);
    t0->tv_nsec = (long)(nsec % 1000000000);
    
    printf("Sleeping for %lu sec, %lu nsec\n", t0->tv_sec, t0->tv_nsec);

    while ((nanosleep(t0, t1) == (-1)) && (errno == EINTR))
    {
        tmp = t0;
        t0 = t1;
        t1 = tmp;
    }
}

int timediff(char* time_str1, char* time_str2){
	struct tm time_tm1 = {0}, time_tm2 = {0};
    sscanf(time_str1, "%d:%d:%d",
           &time_tm1.tm_hour, &time_tm1.tm_min, &time_tm1.tm_sec);
    sscanf(time_str2, "%d:%d:%d",
           &time_tm2.tm_hour, &time_tm2.tm_min, &time_tm2.tm_sec);

    // Adjust year and month for struct tm

    // Convert struct tm to time_t
    time_t time1 = mktime(&time_tm1);
    time_t time2 = mktime(&time_tm2);

    // Calculate time difference
    time_t diff = difftime(time2, time1);

    return (int)diff;
}

char* getTime(char* buffer){
	char *log_buffer = (char *)malloc(1024*sizeof(char));
   	strcpy(log_buffer, buffer);
	int init_size = strlen(log_buffer);
	char delim[] = " ";
	// printf(" - [%s] -", log_buffer);

	char *ptr = strtok(log_buffer, delim);
	ptr = strtok(NULL, delim);
	// printf("'%s'\n", ptr);
	free(log_buffer);

	return ptr;
}

char* getDate(){
	FILE* adb_shell_pipe = popen("(date +'%m-%d %H:%M:%S.000')", "r");
    if (!adb_shell_pipe) {
        printf("Failed to execute adb shell command\n");
        return NULL;
    }

    char* ret = (char *)malloc(19*sizeof(char));;
    // Read the output of the adb shell command
    fgets(ret, 19, adb_shell_pipe);
    ret[18] = '\0';

    // Close the pipe
    pclose(adb_shell_pipe);

    return ret;
}

void waitForWebviews(){
    char log_buffer[1024];
    int first_access_is_done = 0, WAIT = 0, FLAG=0, counter=0, INIT=0;
    char* start_time;

    char* tmp = getDate();
	char date[18];
    char logcat_command[34] = "logcat -d -T '";

	strncat(logcat_command, tmp, 18);
	logcat_command[32] = '\'';
	logcat_command[33] = '\0';

	free(tmp);

	FILE* write_to_logcat = popen("log -p d -t UI-LoadedWebviews \"Init\"", "r");
    if (!write_to_logcat) {
        printf("Failed to open logcat.\n");
        return;
    }
    pclose(write_to_logcat);

    while(1){

    	if (FLAG==1)
    		break;

    	FILE* log_file = popen(logcat_command, "r");
	    if (!log_file) {
	        printf("Failed to open logcat.\n");
	        return;
	    }

	    while (fgets(log_buffer, sizeof(log_buffer), log_file) != NULL) {
	        // if (!first_access_is_done){
	        // 	start_time = getTime(log_buffer);
	        // 	first_access_is_done = 1;
	        // }
	        // else{
	        // 	if (WAIT==0){
	        // 		char* new_time = getTime(log_buffer);
		    //     	if (new_time!=NULL){
		    //     		// printf("%s, %s", start_time, new_time);
		    //     		int difference = timediff(start_time, new_time);
			//         	if (difference>5){
			//         		printf("Timeout Stop...\n");
			//         		FLAG = 1;
			//         		break;
			//         	}
		    //     	}
	        // 	}
	        	
	        // }
	        
	        char* logcat = strstr(log_buffer, "UI-LoadedWebviews");
	        if (logcat!=NULL){
	        	counter+=1;
	            char* wait = strstr(log_buffer, "UI-LoadedWebviews: 0");
	            char* stop = strstr(log_buffer, "UI-LoadedWebviews: 1");
	            char* init = strstr(log_buffer, "UI-LoadedWebviews: Init");
	            // printf("%s", log_buffer);
	            if (wait!=NULL){
	            	WAIT = 1;
	                // printf("%s", "Wait...\n");
	            }
	            else if (stop!=NULL){
	                // printf("%s", "Stop0000000000000000000000000000000000000000000000000000000...\n");
	                FLAG = 1;
	                break;
	            }
	            else if (init!=NULL){
	                INIT += 1;
	            }
	        }

	    }

	    if (counter==INIT && INIT>1 && WAIT==0){
	    	// printf("%s", "Stop2...\n");
	    	break;
	    }

	    // printf("%s", log_buffer);

		// Close logcat
		pclose(log_file);

    }

	

	// printf("%s", "BYE\n");
	
}

// from <linux/input.h>
#define EVIOCGVERSION       _IOR('E', 0x01, int)            /* get driver version */
#define EVIOCGID        _IOR('E', 0x02, struct input_id)    /* get device ID */
#define EVIOCGKEYCODE       _IOR('E', 0x04, int[2])         /* get keycode */
#define EVIOCSKEYCODE       _IOW('E', 0x04, int[2])         /* set keycode */

#define EVIOCGNAME(len)     _IOC(_IOC_READ, 'E', 0x06, len)     /* get device name */
#define EVIOCGPHYS(len)     _IOC(_IOC_READ, 'E', 0x07, len)     /* get physical location */
#define EVIOCGUNIQ(len)     _IOC(_IOC_READ, 'E', 0x08, len)     /* get unique identifier */

#define EVIOCGKEY(len)      _IOC(_IOC_READ, 'E', 0x18, len)     /* get global keystate */
#define EVIOCGLED(len)      _IOC(_IOC_READ, 'E', 0x19, len)     /* get all LEDs */
#define EVIOCGSND(len)      _IOC(_IOC_READ, 'E', 0x1a, len)     /* get all sounds status */
#define EVIOCGSW(len)       _IOC(_IOC_READ, 'E', 0x1b, len)     /* get all switch states */

#define EVIOCGBIT(ev,len)   _IOC(_IOC_READ, 'E', 0x20 + ev, len)    /* get event bits */
#define EVIOCGABS(abs)      _IOR('E', 0x40 + abs, struct input_absinfo)     /* get abs value/limits */
#define EVIOCSABS(abs)      _IOW('E', 0xc0 + abs, struct input_absinfo)     /* set abs value/limits */

#define EVIOCSFF        _IOC(_IOC_WRITE, 'E', 0x80, sizeof(struct ff_effect))   /* send a force effect to a force feedback device */
#define EVIOCRMFF       _IOW('E', 0x81, int)            /* Erase a force effect */
#define EVIOCGEFFECTS       _IOR('E', 0x84, int)            /* Report number of effects playable at the same time */

#define EVIOCGRAB       _IOW('E', 0x90, int)            /* Grab/Release device */

// end <linux/input.h>

#define ARRAYSIZE(x)  (sizeof(x)/sizeof(*(x)))
 

int main(int argc, char *argv[])
{       
        
    if(argc == 1)
    {
        printf("ERROR: Please specify the location of the event file\n\n");
        exit(1);
    }
    
    int returned = 0;   
    long lineNumbers = 0;
    
    FILE *file = fopen(argv[1], "r");
    
    if(file)
    {       
        size_t i, j, k, l, m, x;
            
        char buffer[BUFSIZ], *ptr;              
        fgets(buffer, sizeof buffer, file);     
        ptr = buffer;
        lineNumbers = (long)strtol(ptr, &ptr, 10);
        
        printf("\n\nLine Numbers = %lu\n\n", lineNumbers);
        
        // eventType will then match based on whatever is in the sendEvents.txt file

        unsigned short * eventType;
        unsigned short * codeData;
        unsigned short * typeData;
        unsigned long * valueData;
        uint64_t * timeArray;
        
        eventType = (unsigned short *) calloc((lineNumbers*1), sizeof(unsigned short));
        codeData = (unsigned short *) calloc((lineNumbers*1), sizeof(unsigned short));
        typeData = (unsigned short *) calloc((lineNumbers*1), sizeof(unsigned short));      
        valueData = (unsigned long *) calloc((lineNumbers*1), sizeof(unsigned long));
        timeArray = (uint64_t *) calloc((lineNumbers*1), sizeof(uint64_t));
        
    
        if(eventType == NULL)
            printf("eventType failed malloc\n");
        if(codeData == NULL)
            printf("codeData failed malloc\n");
        if(typeData == NULL)
            printf("typeData failed malloc\n");
        if(valueData == NULL)
            printf("valueData failed malloc\n");
        if(timeArray == NULL)
            printf("timeArray failed malloc\n");
    
        
        int everyOther = 0;
    
        for(i = 0, l = 0, m = 0; fgets(buffer, sizeof buffer, file); ++i)
        {
            if(everyOther == 1)
            {
                for(j = 0, ptr = buffer; j < 4; ++j, ++ptr)
                {
                    if(j == 0)
                        eventType[m] = (unsigned short)strtoul(ptr, &ptr, 10);                      
                    else if(j == 1)
                        codeData[m] = (unsigned short)strtoul(ptr, &ptr, 10);
                    else if(j == 2)
                        typeData[m] = (unsigned short)strtoul(ptr, &ptr, 10);
                    else if(j == 3)
                        valueData[m] = (unsigned long)strtoul(ptr, &ptr, 10);                   
                }
                
                m++;
                everyOther = 0;                 
            }
            else
            {
                ptr = buffer;
                timeArray[l] = (uint64_t)strtoull(ptr, &ptr, 10);       
                everyOther = 1;
                l++;
            }
        }
        fclose(file);

        //========      Start Sending Events        ============
                
        char device[] = "/dev/input/event "; 
        //[16] is for the event input number
        
        char* deviceP = device;
        int fd;
        int wait_for_webviews=0;
        
        j=0,k=0;
        
        // For each of the line numbers get the event, validate it, and then write it
        while(k < lineNumbers)
        {               
            deviceP[16] = eventType[k]+48; //add 48 to get to the ascii char
            fd = open(deviceP, O_RDWR);     

            int ret;
            int version;
        
            // Make sure opening the device opens properly          
            if(fd <= 0) 
            {
                fprintf(stderr, "could not open %s, %s\n", *(&deviceP), strerror(errno));
                return 1;
            }
            
            if (ioctl(fd, EVIOCGVERSION, &version)) 
            {
                fprintf(stderr, "could not get driver version for %s, %s\n", *(&deviceP), strerror(errno));
                return 1;
            }           
            
            struct input_event checkEvent[5];
            int valid = 0;   
                    
            if(timeArray[j] == 0)
            {
                // Prep the event for checking, store the type, code, value in checkEvent
                l = 0;
                while((timeArray[j] == 0) && (j < lineNumbers)) //check the next one, but not if at end of array
                {   
                    checkEvent[l].type = codeData[k];
                    checkEvent[l].code = typeData[k];
                    checkEvent[l].value = valueData[k];
                    j++;
                    k++;
                    l++;
                    valid++;
                }               
            }
            else
            {       
                // Sleep for time interval calculated in Translate
                goSleep(timeArray[j]);
                checkEvent[0].type = codeData[k];
                checkEvent[0].code = typeData[k];
                checkEvent[0].value = valueData[k];
                j++;
                k++;
                valid = 1;
            }

            struct input_event event[valid];
            memset(&event, 0, sizeof(event));
            
            for(x = 0; x < valid; x++)
            {
                event[x].type = checkEvent[x].type;
                event[x].code = checkEvent[x].code;
                event[x].value = checkEvent[x].value;

                //A complete event starts and ends with type==1
                if(checkEvent[x].type == 1){
                    wait_for_webviews = 1;
                }
            }


            if(strncmp(argv[2],"--wait-webviews",15)==0 && wait_for_webviews==1){
                waitForWebviews();
                wait_for_webviews=0;
            }
            // ** Write the event that we just got from checkEvent **
            ret = write(fd, &event, sizeof(event));
                        
            if(ret < sizeof(event)) 
            {
                fprintf(stderr, "write event failed, %s\n", strerror(errno));
                //should exit...                
            }    
            
        }       
    }
    else // fopen() returned NULL
    {
        //perror(filename);
        perror(argv[1]);
    }
    
    return 0;
}
