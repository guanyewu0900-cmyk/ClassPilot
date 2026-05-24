module.exports = {
  apps: [
    {
      name: "classpilot",
      script: "server.js",
      env: {
        NODE_ENV: "production",
        PORT: "5173"
      }
    }
  ]
};
