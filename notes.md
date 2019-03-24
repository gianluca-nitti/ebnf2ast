## "Normalized" form
* Each rule's RHS is either a Sequence or an Alternative
* When a Sequence, can only contain:
	* Identifiers, Literals
	* Optionals
	* Lists
	* -> meaning no Alternatives (referenced via Identifiers)
* When an Alternative, can only contain Identifiers
* Each part of a Sequence has a unique name (excluding literals)

* Sequence -> class
* Alternative -> abstract class w/ subclasses for each alt
* Eveything else -> class member
