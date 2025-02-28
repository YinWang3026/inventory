# Dockerfile for Development

# DevOps Workshop 2021 Image for Python3 and Docker
FROM python:3.8-slim

ARG INSTALL_ZSH="true"
ARG UPGRADE_PACKAGES="false"
ARG ENABLE_NONROOT_DOCKER="true"
ARG USE_MOBY="true"
ARG DOCKER_VERSION="latest"

# Enable new "BUILDKIT" mode for Docker CLI
ENV DOCKER_BUILDKIT=1

# Create a user for development
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

COPY .devcontainer/library-scripts/*.sh /tmp/library-scripts/
RUN apt-get update \
    && /bin/bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" "true" "true" \
    # Use Docker script from script library to set things up
    && /bin/bash /tmp/library-scripts/docker-in-docker-debian.sh "${ENABLE_NONROOT_DOCKER}" "${USERNAME}" "${USE_MOBY}" "${DOCKER_VERSION}" \
    # gcc
    && apt-get install -y libpq-dev gcc \
    # Need PostgreSQL development library to compile on arm64
    && apt-get install -y libpq-dev \
    # Install Chromium Driver
    && apt-get install -y chromium-driver \
    # Clean up
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts/

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# Set up the Kubernetes and IBM Cloud tools
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/$(dpkg --print-architecture)/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && echo "alias kc='/usr/local/bin/kubectl'" >> /home/$USERNAME/.bash_aliases \
    && chown $USERNAME:$USERNAME /home/$USERNAME/.bash_aliases \
    && curl -s https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash \
    && curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash \
    && if [ $(dpkg --print-architecture) = 'amd64' ]; then curl -fsSL https://clis.cloud.ibm.com/install/linux | sh; fi;    

# Set up the development environment
WORKDIR /app
COPY ../requirements.txt .
RUN pip install -U pip wheel setuptools \
    && pip install -r requirements.txt \
    && rm -f requirements.txt
VOLUME [ "/var/lib/docker" ]

# Become a regular user
USER $USERNAME

# IBM Cloud plugins must be installed by the user
RUN if [ $(dpkg --print-architecture) = 'amd64' ]; then \
        ibmcloud plugin install container-service; \
        ibmcloud plugin install container-registry; \
    fi;    

# Setting the ENTRYPOINT to docker-init.sh will start up the Docker Engine 
# inside the container "overrideCommand": false is set in devcontainer.json. 
# The script will also execute CMD if you need to alter startup behaviors.
ENTRYPOINT [ "/usr/local/share/docker-init.sh" ]
CMD [ "sleep", "infinity" ]
