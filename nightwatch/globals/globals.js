// global vars for testing wellness 2.0
// this would cover some basic vars or dynamic "fuzzy"
// variables we could generate w/ the crypto library
// if we want to throw in random dates, stair climbs etc
// and then validate the result from that fuzz test

var crypto = require("crypto");

// non-env specific variables
var websiteTitle = 'React App'

/// local
var webUrlLocal = 'http://localhost:3000'

/// dev
var webUrlDev = 'http://s3-bucket-website-s3bucket-p21b25cdh40n.s3-website-us-east-1.amazonaws.com'

/// prod
var webUrlProd = 'https://effinglegs.rip'

module.exports = {
    websiteTitle: websiteTitle,

    // default is for localhost testing
    'default': {
        url: webUrlLocal,
    },
    'dev': {
        url: webUrlDev,
    },
    'prod': {
        url: webUrlProd,
    },

    // default globals being modified
    // Automatically retrying failed assertions
    retryAssertionTimeout: 5000,
}
