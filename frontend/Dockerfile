FROM node:22-alpine

WORKDIR /srv/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend /srv/frontend

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
