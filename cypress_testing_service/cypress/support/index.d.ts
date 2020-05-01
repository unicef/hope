declare namespace Cypress {
    interface Chainable {
       loginToAD(username: string, password: string, url: string): Chainable<Element>
    }
}
