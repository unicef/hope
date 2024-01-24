const path = require('path');
const fs = require('fs');

class DjangoTagsPlugin {
  constructor(options) {
    this.options = options;
  }

  apply(compiler) {
    compiler.hooks.done.tapAsync('DjangoTagsPlugin', (stats, callback) => {
      const tagToSearch = compiler.options.output.publicPath;
      const outputPath = compiler.options.output.path;
      const indexPath = path.join(outputPath, 'index.html');
      const targetPath = path.join(
        this.options.djangoTemplatePath,
        'index.html',
      );

      // Read index.html
      fs.readFile(indexPath, 'utf8', (err, data) => {
        if (err) {
          console.error(err);
          return callback();
        }


        const modifiedData = data.replaceAll(new RegExp(tagToSearch+"\\/(.*?)\"","g"), `{% static "/${this.options.djangoAppName}/$1" %}"`);
        console.log("Modified index.html");
        fs.writeFile(targetPath, modifiedData, 'utf8', (writeErr) => {
          if (writeErr) {
            console.error(writeErr);
            return callback();
          }

          // Delete the original file
          fs.unlink(indexPath, (unlinkErr) => {
            if (unlinkErr) {
              console.error(unlinkErr);
            }
            callback();
          });
        });
      });
    });
  }
}

module.exports = DjangoTagsPlugin;
