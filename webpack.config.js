const path = require('path');

module.exports = {
  entry: './javascript/index.js',
  output: {
    filename: './main.js',
    path: path.resolve(__dirname, 'javascript'),
  },
  mode: "development",
  module: {
	  rules: [
		  {
			  test: /\.(js)$/,
			  exclude: /node_modules/,
			  use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            cacheDirectory: true
          }
        }
		  }
	  ]
  },
  resolve: {
	  extensions: ['*', '.js']
  },
  cache: true
};