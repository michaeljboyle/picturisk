/*jshint esversion: 6 */
/**
 * HTTP Cloud Function.
 *
 * @param {Object} req Cloud Function request context.
 * @param {Object} res Cloud Function response context.
 */

const svg2png = require('svg2png');

exports.convertSVG = function convertSVG(req, res) {
    console.log(req.body);
    buffer = req.body;
    res.writeHead(200, {'Content-Type': 'image/png'});
    svg2png(buffer)
        .then(buffer => res.end(buffer))
        .catch(e => console.error(e)); 
};