# outfox-frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package.json and yarn.lock (or package-lock.json) and install dependencies
# This step is done separately to leverage Docker cache
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
# If you are using npm, use:
# COPY package.json package-lock.json ./
# RUN npm install --ci

# Copy the rest of the frontend application code
COPY . .

# Expose the port React development server runs on
EXPOSE 3000

# Command to start the React development server
CMD ["yarn", "start"]
# If you are using npm, use:
# CMD ["npm", "start"]
