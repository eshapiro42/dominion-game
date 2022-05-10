<script>
    import {socket} from "../stores.js";

    let tradeRoute = false;
    let prizes = false;

    $socket.on(
        "trade route",
        (data) => {
            tradeRoute = true;
        }
    );

    $socket.on(
        "prizes",
        (data) => {
            prizes = true;
        }
    )
</script>

<main>
    <a class="section" href="#Played Cards">Active</a>
    <a class="section" href="#Your Hand">Hand</a>
    <a class="section" href="#Supply">Supply</a>
    <a class="section" href="#Your Discard Pile">Discard</a>
    <a class="section" href="#Trash">Trash</a>
    {#if prizes}
        <a class="section" href="#Prizes">Prizes</a>
    {/if}
    {#if (tradeRoute)}
        <a class="section" href="#Trade Route">Trade Route</a>
    {/if}
    <a class="section" href="#Player Info">Players</a>
</main>

<style>
    main {
        left: 0;
        top: 0;
        width: 64px;
        height: 100%;
        position: fixed;
        background-color: #343338;
        color: #dadada;
        display: flex;
        flex-direction: column;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: space-around;
        align-items: stretch;
    }

    /* Do not show sidebar on mobile devices */
    @media (max-width: 767px) {
        main {
             display: none;
        }
    }

    .section {
        justify-content: center;
        align-items: center;
        display: flex;
        writing-mode: vertical-lr;
        transform: rotate(180deg);
        font-weight: bold;
        flex-grow: 1;
        font-size: 20px;
    }

    .section:hover {
        background-color: #605e67;
    }

    a {
        color: #dadada;
    }

    a:hover {
        text-decoration: none;
    }
</style>