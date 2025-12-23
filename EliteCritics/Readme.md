# 🎬 Elite Critics - Project Blueprint

Elite Critics is a film rating system that recalculates the Rotten Tomatoes (RT) Tomatometer (Critics) score, assigning different weights to reviews based on the critic's experience and ranking in specific genres.

## ⚙️ Program Entry

* **Film Name:** The name (or *slug*) of the film to be analyzed (e.g., `twilight` for the 2008 film).

## 🗄️ Database Structure (SQLite)

* **Convention:** Table names in **singular** (`Film`, `Critic`, `Criticism`).

* **Film Table:** Stores film data.

* `url_filme (TEXT) (PK)`: Primary key. Example: `/m/twilight` or `/m/1082855-twilight`.

* `name (TEXT)`: Full name of the movie.
* `rt_rating (INTEGER)`: Original RT Tomatometer score.
* `popcornmeter_rating (INTEGER)`: Original RT Popcornmeter score.
* `ndci_rating (REAL)`: Critics' Score I - *No Room for Noobies* (Under Construction).
* `ndci_rating (REAL)`: Critics' Score II - *Hierarchy* (Under Construction).
* `genres (TEXT)`: Movie genres, separated by commas (e.g., 'Kids & Family, Musical, Fantasy').
* **Critic Table:** Stores critic data and experience.
* `critic_url (TEXT) (PK)`: Primary key. Example: `/critics/critic-name/movies`.
* `name (TEXT)`: Full name of the critic.
* `genre_experience (TEXT)`: JSON or serialized string that stores the experience by genre (e.g., `{"Fantasy": 55, "Musical": 2, ...}`).
* `genre_rank (TEXT)`: JSON or serialized string that stores the ranking by genre (e.g., `{"Fantasy": 3, "Musical": 0, ...}`).

* **Critic Table:** Stores the ratings of each critic.

* `id (INTEGER) (PK)`: Incremental primary key.

* `critic_url (TEXT) (FK)`: Foreign key to the `Critic` table.

* `movie_url (TEXT) (FK)`: Foreign key to the `Movie` table. * `approval (BOOLEAN)`: `True` (Fresh/Positive) or `False` (Rotten/Negative).

## 🗺️ Web Scraping and Processing Flow

1. **Input:** User enters the `movie_name`.

2. **Web Scraping I (Input Movie):**
* URL: `https://www.rottentomatoes.com/m/movie_name` (using `_`).

* **Action:**
* Get `rt_score`, `genres`, and the actual URL (*slug*) of the movie (handling duplication, e.g., `twilight` vs. `1082855-twilight`).

* **Check Cache/Database:** Use the URL as a key to check if the movie already exists. If it doesn't exist, save it to the **Movie** table.

3. **Web Scraping II (Reviews):**
* URL: `https://www.rottentomatoes.com/m/movie_name/reviews`.
* **Action:**
* Get the list of all critics and their `approval (bool)` for the incoming movie.
* **Attention:** Handle pagination (*Load More*) to load all reviews.
* 4. **Processing and Web Scraping III (Critic Experience):**
* **Loop 1 (Per Critic):** For each critic found:
* **Check Cache/DB:** Use the critic's URL to check if the critic already exists and if the experience by genre has been calculated.
* **If NEW Critic:**
* Web Scraping III: Access `https://www.rottentomatoes.com/critics/critic-name/movies` (using `-`).

** * **Attention:** Handle pagination (*Load More*) to obtain the complete list of films reviewed by this critic.

* **Loop 2 (Per Film Reviewed):** For each film reviewed:

* Obtain the film's URL.
* **Local Database Query:** Search for the film's genre in the **Film** table.

* **If Genre NOT FOUND:** Perform point-by-point *Web Scraping* of the film's page and save the genre in the **Film** table.

* **Calculate EXP:** If the genres of the reviewed film and the input film (`#1`) overlap (even if only one), increment the critic's experience in that genre(s).

* Calculate the critic's **Rank** based on experience by genre and save it in the **Critic** table.

5. **Score Calculation (Output):**
* **NDCI (Coming Soon):** Recalculate the score excluding reviews from Rank 0 critics in the relevant genre(s).

* **NDCII (Coming Soon):** Recalculate the score applying weights according to the critic's Rank in the relevant genre(s).

## 🏆 Output

* Tomatometer (RT)
* Popcornmeter (RT)
* Critic Score I - no room for noobies (NDCI) **(Coming Soon/Under Construction)**
* Critic Score II - hierarchy (NDCII) **(Coming Soon/Under Construction)**