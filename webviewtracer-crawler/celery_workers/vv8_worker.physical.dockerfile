FROM python:3.10

USER root

RUN apt-get update && apt install -y lsb-release;
RUN apt-get update && apt install -y tar xz-utils wget unzip zip curl htop vim;
WORKDIR /tmp/android-tools
RUN wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip && unzip platform-tools-latest-linux.zip
RUN mv platform-tools/* /usr/bin
# Add working dir to python path
ENV PYTHONPATH "${PYTHONPATH}:/app"

WORKDIR /
VOLUME /app/uiharvester
COPY vv8_worker/uiharvester /app/uiharvester
RUN pip install --no-cache-dir --upgrade -r /app/uiharvester/requirements.txt
RUN pip install frida==16.4.10 frida-tools;
RUN wget -O /tmp/frida-server.xz https://github.com/frida/frida/releases/download/16.4.10/frida-server-16.4.10-android-arm64.xz
RUN unxz /tmp/frida-server.xz && mv /tmp/frida-server /app/frida-server
# Install python modules
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

RUN rm -rf /app/uiharvester

ENV DISPLAY :99
ENV XDG_CURRENT_DESKTOP XFCE

RUN apt update && \
    apt install -y curl && \
    apt install -y --no-install-recommends xvfb && \
    apt install -y --no-install-recommends xauth && \
    apt install -y libnss3-dev && \
    apt install -y libgbm-dev && \
    apt install -y libasound2-dev && \
    apt install -y --no-install-recommends xfce4 && \
    apt install -y --no-install-recommends xdg-utils && \
    apt-get install -y tigervnc-standalone-server && \
    apt install -y tigervnc-common && \ 
    apt install -y gnome-terminal && \
    apt install -y procps

RUN apt install -y ffmpeg libsdl2-2.0-0 wget \
gcc git pkg-config meson ninja-build libsdl2-dev \
libavcodec-dev libavdevice-dev libavformat-dev dbus-x11 libavutil-dev \
libswresample-dev libusb-1.0-0 libusb-1.0-0-dev sudo

RUN git clone https://github.com/Genymobile/scrcpy && cd scrcpy && ./install_release.sh

RUN groupadd -g 1001 -f vv8; \
    useradd -u 1001 -g 1001 -s /bin/bash -m vv8
ENV PATH="${PATH}:/home/vv8/.local/bin"

RUN git clone --branch v1.4.0 --single-branch https://github.com/novnc/noVNC.git /opt/noVNC; \
    git clone --branch v0.11.0 --single-branch https://github.com/novnc/websockify.git /opt/noVNC/utils/websockify; \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html

# Copy app
COPY ./vv8_worker /app/vv8_worker
COPY ./vv8_worker/adb-service.sh /app/adb-service.sh
COPY ./vv8_worker/entrypoint.sh /app/entrypoint.sh
COPY ./vv8_worker/nuke.sh /app/nuke.sh
RUN chmod +x /app/*.sh

ENV DISPLAY :99

ENV DISPLAY=:1 \
    VNC_PORT=5901 \
    NO_VNC_PORT=6901 \
    VNC_COL_DEPTH=32 \
    VNC_RESOLUTION=1920x1080

CMD ["/app/entrypoint.sh"]
