const path = require('path');

module.exports = {
  entry: './javascript/index.js',
  output: {
    filename: './main.js',
    path: path.resolve(__dirname, 'javascript'),
  },
  mode: "production",
  module: {
	  rules: [
		  {
			  test: /\.(js)$/,
			  exclude: /node_modules/,
			  use: ['babel-loader']
		  }
	  ]
  },
  resolve: {
	  extensions: ['*', '.js']
  }
};