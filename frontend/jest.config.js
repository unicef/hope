module.exports = {
    collectCoverage: true,
    collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}'],
    moduleDirectories: ['node_modules', 'src'],
    testPathIgnorePatterns: [
        '/node_modules/',
        '/.history/',
        '/scripts/'],
    setupFilesAfterEnv: ['./jest/setupTests.ts'],
    transform: {
        "^.+\\.(js|jsx|ts|tsx)$": "<rootDir>/node_modules/babel-jest",
        "^.+\\.css$": "<rootDir>/config/jest/cssTransform.js",
        "^(?!.*\\.(js|jsx|ts|tsx|css|json)$)": "<rootDir>/config/jest/fileTransform.js"
    },
    transformIgnorePatterns: [
        "[/\\\\]node_modules[/\\\\].+\\.(js|jsx|ts|tsx)$",
        "^.+\\.module\\.(css|sass|scss)$"
    ],
    coveragePathIgnorePatterns: [
        '/node_modules/.*',
        '/script/',
        '/src/serviceWorker.ts',
        '.*\\.d\\.ts'
    ],
};
