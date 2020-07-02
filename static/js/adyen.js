// Structure credit card payment request
const structureRequest = (data) => {

    const paymentRequest = {
        paymentMethod: data.paymentMethod
    };

    if (data.paymentMethod.type === "scheme") {
        paymentRequest['billingAddress'] = data.billingAddress;
        paymentRequest['browserInfo'] = data.browserInfo;
    }

    return paymentRequest;
};

// Parse payment response and directing shopper to correct place
const handleFinalState = (resultCode) => {
    if (resultCode === 'Authorised') {
        window.location.href = "http://localhost:8000/success";

    } else if (resultCode === 'Pending' || resultCode === 'Received') {
        window.location.href = "http://localhost:8000/pending";

    } else if (resultCode === 'Error') {
        window.location.href = "http://localhost:8000/error";

    } else {
        console.log("failed");
        window.location.href = "http://localhost:8000/failed";
    }
};

/*
 * Dropin and Component event handlers
 *
 * And Create Adyen checkout method
 */

const onSubmit = (state, component) => {
    console.log("Sending Payment Request");
    fetch('/initiatePayment/', {
        method: 'POST',
        headers: {
            Accept: 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(structureRequest(state.data))
    }).then(response => response.json())
        .then(response => {
            if (response.action) {
                if (response.resultCode === 'RedirectShopper') {
                    localStorage.setItem('redirectPaymentData', response.action.paymentData);
                }
                adyenComponent.handleAction(response.action);

            } else {
                handleFinalState(response.resultCode);
            }
        })
        .catch(error => {
            console.log("error");
            window.location.href = "http://localhost:8000/failed";
        });
};

const onAdditionalDetails = (state, component) => {
    console.log("On additionalDetails triggered");
    fetch('/submitAdditionalDetails/', {
        method: 'POST',
        headers: {
            Accept: 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(state.data)
    }).then(response => response.json())
        .then(response => {
            if (response.action) {
                adyenComponent.handleAction(response.action);
            } else {
                handleFinalState(response.resultCode);
            }
        })
        .catch(error => {
            console.log(error);
            window.location.href = "http://localhost:8000/failed";
        });
};

const onError = (error) => {
    console.log(error);
};


// Create Adyen checkout instance and initilize component
const createAdyenCheckout = () => {
        // Get /paymentMethods call and originKey response Jinja2 passed back to <script> tag
        // Need to run JSON.parse() 2x because Jinja2 |tojson filter stringifies /paymentMethod response again. However,
        // not including this filter results in an HTML encoded string
        const paymentMethods = JSON.parse(JSON.parse(document.getElementById('payment-methods').innerHTML));
        const originKey = JSON.parse(document.getElementById('origin-key').innerHTML);

        // Placeholder values
        const translations = {
            // "en-US": {
            //     "creditCard.numberField.title": "Custom Card Name",
            // }
        };

        const paymentMethodsConfiguration = {
            card: { // Example optional configuration for Cards
                //hideCVC: true, // Change this to true to hide the CVC field for stored cards. false is default
                // placeholders: { # Change placeholder text for the following fields
                // encryptedCardNumber: "",
                // encryptedSecurityCode: ""
                // },
                //billingAddressRequired: true,
                hasHolderName: true,
                holderNameRequired: true,
                enableStoreDetails: true,
                name: 'Credit or debit card'
            },
            ach: { // Default ACH user information
                holderName: 'Ach User',
                billingAddressRequired: false
                // data: {
                //     billingAddress: {
                //         street: 'Infinite Loop',
                //         postalCode: '95014',
                //         city: 'Cupertino',
                //         houseNumberOrName: '1',
                //         country: 'US',
                //         stateOrProvince: 'CA'
                //     }
                // }
            },
            paypal: {
                amount: {
                    currency: "USD",
                    value: 1000
                },
                environment: "test", // Change this to "live" when you're ready to accept live PayPal payments
                countryCode: "US", // Only needed for test. This will be automatically retrieved when you are in production.
                intent: "capture", // Change this to "authorize" if the payments should not be captured immediately. Contact Support to enable this flow.
            }
        };

        const configObj = {
            paymentMethodsConfiguration: paymentMethodsConfiguration,
            showPayButton: true,
            locale: "en_US",
            environment: "test",
            originKey: originKey,
            paymentMethodsResponse: paymentMethods,
            translations: translations,
            onSubmit: onSubmit,
            onAdditionalDetails: onAdditionalDetails,
            onError: onError
        };
        return new AdyenCheckout(configObj);
    }
;


const checkout = createAdyenCheckout();
const adyenComponent = checkout.create('dropin').mount("#dropin-container");

