const xlsx = require('node-xlsx').default;
const fileSys = require('fs');

const filePath = process.argv[2];
console.log(process.argv);
const jsonData = xlsx.parse(fileSys.readFileSync(filePath))[0];
const rows = jsonData.data;

console.log('ROWS', rows);

for (let i = 1; i < rows.length; i++) {
  if (rows[i].length !== 0) {
    // add delivered column and write value of 100
    rows[i].push(100);
  }
}

xlsx.build([{ name: jsonData.name, data: rows }]);
const buffer = xlsx.build([{ name: jsonData.name, data: rows }]);

const index = filePath.lastIndexOf('/');
const leftWithDownloads = filePath.slice(0, index - 1);
const left = leftWithDownloads.slice(0, leftWithDownloads.lastIndexOf('/'));
const right = filePath.slice(index + 1);

const outputFileName = `${left}/fixtures/out_${right}`;

fileSys.writeFileSync(outputFileName, buffer);
