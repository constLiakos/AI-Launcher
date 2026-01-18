const fs = require('fs');
const path = require('path');

const packagePath = path.join(__dirname, '..', 'package.json');
const readmePath = path.join(__dirname, '..', 'README.md');

const packageJson = require(packagePath);
const newVersion = packageJson.version;

console.log(`Updating README to version: ${newVersion}`);

let readmeContent = fs.readFileSync(readmePath, 'utf8');

const regex = /badge\/version-v\d+\.\d+\.\d+(?:(?:-|--)[a-zA-Z0-9.-]+)?-blue/g;

const safeVersion = newVersion.replace(/-/g, '--');
const replacement = `badge/version-v${safeVersion}-blue`;

if (readmeContent.match(regex)) {
    readmeContent = readmeContent.replace(regex, replacement);
    fs.writeFileSync(readmePath, readmeContent);
    console.log('✅ README.md updated successfully.');
} else {
    console.warn('⚠️  Warning: Version badge not found in README.md');
}