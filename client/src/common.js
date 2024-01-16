function compareProperties(a, b, property) {
    //  Compare a given property of two cards
    if (a[property] < b[property]) {
        return -1;
    }
    if (a[property] > b[property]) {
        return 1;
    }
    return 0;
}

function compareCards(a, b, sortByProperty, previousProperty=null) {
    /*  Compare two cards based on a given card property

        Allowable properties:
            "cost"
            "name"
            "type"
            "orderSent"

        Properties "type" and "cost" are each other's tie breakers by default

        The "previousProperty" parameter is to prevent infinite recursion from these tie breakers

        The last resort tie breaker is "name"
    */
    if (sortByProperty == "orderSent") {
        return 0;
    }
    const comparison = compareProperties(a, b, sortByProperty);
    if (comparison != 0) {
        return comparison;
    }
    // Tie breakers 
    if (sortByProperty == "type") {
        if (previousProperty != "cost") {
            return compareCards(a, b, "cost", "type");
        }
        return compareCards(a, b, "name");
    }
    if (sortByProperty == "cost") {
        if (previousProperty != "type") {
            return compareCards(a, b, "type", "cost");
        }
        return compareCards(a, b, "name");
    }
    return 0;
};

export function sortCards(cards, sortByProperty, victoryCardsFirst=false) {
    if (victoryCardsFirst) {
        let victoryCards = cards.filter(card => card.types.includes("victory") || card.types.includes("curse"));
        let otherCards = cards.filter(card => !victoryCards.includes(card));
        return sortCards(victoryCards, sortByProperty).concat(sortCards(otherCards, sortByProperty));
    }
    return cards.sort(
        (a, b) => compareCards(a, b, sortByProperty));
};

export function sticky(node) {
    const stickySentinelStyle = "position: absolute; height: 1px;"
    const stickySentinel = document.createElement("div");
    stickySentinel.classList.add("stickySentinel");
    stickySentinel.style = stickySentinelStyle;
    node.parentNode.insertBefore(stickySentinel, node);

    const intersectionCallback = function(entries) {
        // only observing one item at a time
        const entry = entries[0];
        let isStuck = !entry.isIntersecting;
        node.dispatchEvent(
            new CustomEvent('stuck', {
                detail: {isStuck}
            })
        );
    };

    const intersectionObserver = new IntersectionObserver(intersectionCallback, {});

    intersectionObserver.observe(stickySentinel);
}