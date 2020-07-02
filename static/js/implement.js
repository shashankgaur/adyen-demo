// Adyen Drop-in API implementation

const configuration = {
    paymentMethodsResponse: JSON.parse(JSON.parse(document.getElementById('payment-methods').innerHTML)),
    originKey: JSON.parse(document.getElementById('origin-key').textContent),
    locale: "en-US",
    environment: "test",

    onSubmit: (state, dropin) => {
        console.log("onSubmit called")

        if (state.isValid) {
            console.log("State is Valid. API is called:")
            fetch('/initiatePayment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(state.data)
            }).then(response => response.json())
                .then(response => actionState(response))
                .catch(error => console.log(error))
        } else {
            console.log("Drop-in state is invalid.")
        }
    },

    onAdditionalDetails: (state, dropin) => {
        alert("onAdditionalDetails called")

        /* not implemented

        // Your function calling your server to make a `/payments/details` request
        makeDetailsCall(state.data)
            .then(response => {
                if (response.action) {
                    // Drop-in handles the action object from the /payments response
                    dropin.handleAction(response.action);
                } else {
                    // Your function to show the final result to the shopper
                    showFinalResult(response);
                }
            })
            .catch(error => {
                throw Error(error);
            });

         */
    },

    paymentMethodsConfiguration: {
        // List here https://docs.adyen.com/payment-methods
        card: {
            hasHolderName: true,
            holderNameRequired: true,
        }
    }
};

const checkout = new AdyenCheckout(configuration);
const dropin = checkout.create('dropin').mount('#dropin-container');
