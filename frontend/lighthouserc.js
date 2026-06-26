# Lighthouse CI — performance and accessibility gates for TMB frontend
module.exports = {
  ci: {
    collect: {
      url: ["http://localhost:3000/", "http://localhost:3000/verify"],
      numberOfRuns: 1,
      startServerCommand: "npm run start",
      startServerReadyPattern: "Ready",
      startServerReadyTimeout: 120000,
    },
    assert: {
      assertions: {
        "categories:performance": ["warn", { minScore: 0.75 }],
        "categories:accessibility": ["warn", { minScore: 0.9 }],
        "categories:best-practices": ["warn", { minScore: 0.85 }],
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
