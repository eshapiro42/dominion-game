export default function sortCards(cards, sortByProperty, victoryCardsFirst=false) {
    if (victoryCardsFirst) {
        let victoryCards = cards.filter(card => card.types.includes("victory") || card.types.includes("curse"));
        let otherCards = cards.filter(card => !victoryCards.includes(card));
        return sortCards(victoryCards, sortByProperty).concat(sortCards(otherCards, sortByProperty));
    }
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