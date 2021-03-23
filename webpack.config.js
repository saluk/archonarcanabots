const path = require('path');

module.exports = {
  entry: {
    indexCommon: './javascript/index-common.js',
    indexDeckView: './javascript/index-deckView.js',
    indexGallery: './javascript/index-gallery.js',
    indexDeckSearch: './javascript/index-deckSearch.js',
    indexQuick: './javascript/index-quick.js'
  },
  output: {
    filename: './main.[name].js',
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