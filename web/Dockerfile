FROM public.ecr.aws/docker/library/node:22.20.0-alpine3.22 AS build
WORKDIR /web
COPY package*.json ./
COPY .npmrc ./
RUN npm ci
COPY . .
RUN npm run build
FROM public.ecr.aws/docker/library/nginx:1.28.0-alpine
COPY --from=build /web/dist /usr/share/nginx/html
EXPOSE 8080
