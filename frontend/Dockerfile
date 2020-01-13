FROM node:latest

WORKDIR /app
COPY package.json ./package.json
RUN npm i @angular/cli -g
COPY . /app

RUN rm -rf node_modules

RUN npm cache verify
RUN npm install
RUN npm run build

FROM nginx:latest
WORKDIR /app
COPY --from=0  /app/dist/event-detection-frontend .
RUN  rm -rf /usr/share/nginx/html/* && cp -R /app/* /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
