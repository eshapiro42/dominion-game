export default function sortCards(cards, sortByProperty) {
    return cards.sort(
        (a, b) => {
            if (sortByProperty == "orderSent") {
                return 0;
            }
            if (a[sortByProperty] < b[sortByProperty]) {
                return -1;
            }
            else if (a[sortByProperty] > b[sortByProperty]) {
                return 1;
            }
            else {
                return 0;
            }
        }
    )
};