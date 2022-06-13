module.exports = {
    'Login/logout as test Admin User' : function (browser) {
        browser
            .url(browser.globals.url)
            .waitForElementVisible('body', 2000)
            .assert.titleEquals(browser.globals.websiteTitle)
            //.loginUser(browser.globals.userEmail, browser.globals.userPw)
            //.logoutUser()
            .end()
    }
}