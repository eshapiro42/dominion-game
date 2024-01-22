<script>
    export let name;
    export let displayAs = "row";
    export let sortByProperty = "type";
    export let illegalSortByOptions = [];

    let sortByOptions = [
        {text: "Type", property: "type"},
        {text: "Cost", property: "cost"},
        {text: "Name", property: "name"},
        {text: "Order Sent", property: "orderSent"},
    ]

    illegalSortByOptions.forEach(
        (illegalOption) => {
            sortByOptions = sortByOptions.filter((option) => option.property !== illegalOption);
        }
    );

    function getPreferredDisplayOptions() {
        let cachedDisplayOptions = JSON.parse(localStorage.getItem("displayOptions"));
        name = name.includes("Played Cards") ? "Played Cards" : name;
        if (!cachedDisplayOptions || !cachedDisplayOptions.hasOwnProperty(name)) {
            return;
        }
        displayAs = cachedDisplayOptions[name].displayAs;
        sortByProperty = cachedDisplayOptions[name].sortByProperty;
    }

    getPreferredDisplayOptions();

    $: {
        let cachedDisplayOptions = JSON.parse(localStorage.getItem("displayOptions")) ? JSON.parse(localStorage.getItem("displayOptions")) : {};
        name = name.includes("Played Cards") ? "Played Cards" : name;
        cachedDisplayOptions[name] = {
            displayAs: displayAs,
            sortByProperty: sortByProperty,
        };
        localStorage.setItem("displayOptions", JSON.stringify(cachedDisplayOptions));
    }
</script>

<main>
    <div class="dropdowns">
        <div class="sort">
            <p>Sort By<p>
            <select bind:value={sortByProperty}>
                {#each sortByOptions as option}
                    <option value={option.property}>
                        {option.text}
                    </option>
                {/each}
            </select>
        </div>
        <div class="displayAs">
            <p>Display As<p>
            <select bind:value={displayAs}>
                <option value="row">Row</option>
                <option value="grid">Grid</option>
            </select>
        </div>
    </div>
</main>

<style>
    .dropdowns {
        display: flex;
        justify-content: center;
        gap: 100px;
    }

    .sort, .displayAs {
        margin-top: 25px;
        display: flex;
        justify-content: center;
        align-items: baseline;
        flex-wrap: nowrap;
        gap: 10px;
    }

</style>