<script>
    export let name;
    export let displayAs = "row";
    export let sortByProperty = "type";
    export let illegalSortByOptions = [];
    export let show = false;

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

    function toggleCardDisplayOptions() {
        show = !show;
        if (show) {
            document.body.addEventListener('click', toggleCardDisplayOptions);
        }
        else{
            document.body.removeEventListener('click', toggleCardDisplayOptions);
        }
    }

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

<i class="fa-solid fa-gear"
    class:show
    on:click|stopPropagation={toggleCardDisplayOptions}
>
</i>
{#if show}
    <main
        on:click|stopPropagation={()=>{}}
    >
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
{/if}

<style>
    .dropdowns {
        position: absolute;
        z-index: 999;
        display: flex;
        flex-direction: column;
        gap: 5px;
        align-items: end;
        padding: 10px;
        height: auto;
        margin: 5px;
        max-height: 50vh;
        background-color: var(--thead-background-color);
        color: var(--light-text-color);
        border: 1px solid var(--border-color);
        overflow-y: auto;
        right: 10px;
        top: 42px;
    }

    .sort, .displayAs {
        display: flex;
        justify-content: center;
        align-items: baseline;
        flex-wrap: nowrap;
        gap: 10px;
    }

    p {
        margin: 0px;
    }

    .fa-gear {
        position: absolute;
        right: 20px;
        top: 20px;
        z-index: 999;
    }

    .fa-gear:hover {
        cursor: pointer;
    }

    .show {
        color: var(--blue-color);
    }

</style>