// Custom transformer to replace import.meta.env with globalThis.import.meta.env
const babelJest = require('babel-jest').default;

module.exports = babelJest.createTransformer({
  presets: [
    ['@babel/preset-typescript', { jsx: 'react-jsx' }],
  ],
  plugins: [
    function() {
      return {
        visitor: {
          MemberExpression(path) {
            // Replace import.meta.env with globalThis.import.meta.env
            if (
              path.node.object &&
              path.node.object.type === 'MetaProperty' &&
              path.node.object.meta.name === 'import' &&
              path.node.object.property.name === 'meta'
            ) {
              path.replaceWithSourceString('globalThis.import.meta.env');
            }
          },
        },
      };
    },
  ],
});
